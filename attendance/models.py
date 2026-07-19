import io
import uuid

import qrcode
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone


class AttendanceSession(models.Model):
    timetable_entry = models.ForeignKey(
        "academics.TimetableEntry",
        on_delete=models.CASCADE,
        related_name="attendance_sessions",
    )
    session_date = models.DateField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_attendance_sessions",
    )
    allow_manual = models.BooleanField(default=True)
    allow_qr = models.BooleanField(default=True)
    face_recognition_enabled = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    qr_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    qr_image = models.ImageField(upload_to="qr/attendance/", blank=True)
    qr_expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-session_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["timetable_entry", "session_date"],
                name="unique_attendance_session",
            )
        ]

    def save(self, *args, **kwargs):
        update_fields = kwargs.get("update_fields")
        generating_only = update_fields and "qr_image" in update_fields and len(update_fields) == 1
        super().save(*args, **kwargs)
        if not self.qr_image and not generating_only:
            self._generate_qr_code()

    def _generate_qr_code(self):
        payload = f"attendance:{self.pk}:{self.qr_token}"
        image = qrcode.make(payload)
        stream = io.BytesIO()
        image.save(stream, format="PNG")
        self.qr_image.save(
            f"attendance-{self.pk}.png",
            ContentFile(stream.getvalue()),
            save=False,
        )
        super().save(update_fields=["qr_image"])

    def __str__(self) -> str:
        return f"{self.timetable_entry} @ {self.session_date}"


class QRGenerationLog(models.Model):
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name="qr_logs")
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="qr_generation_logs"
    )
    ip_address = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        user = self.requested_by.username if self.requested_by else "anonymous"
        return f"QR log for session {self.session_id} by {user} at {self.created_at}"


class AttendanceRecord(models.Model):
    STATUS_PRESENT = "present"
    STATUS_ABSENT = "absent"
    STATUS_LATE = "late"
    STATUS_EXCUSED = "excused"

    STATUS_CHOICES = [
        (STATUS_PRESENT, "Present"),
        (STATUS_ABSENT, "Absent"),
        (STATUS_LATE, "Late"),
        (STATUS_EXCUSED, "Excused"),
    ]

    METHOD_MANUAL = "manual"
    METHOD_QR = "qr"
    METHOD_FACE = "face"

    METHOD_CHOICES = [
        (METHOD_MANUAL, "Manual"),
        (METHOD_QR, "QR"),
        (METHOD_FACE, "Face Recognition"),
    ]

    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name="records")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attendance_records")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PRESENT)
    access_method = models.CharField(max_length=20, choices=METHOD_CHOICES, default=METHOD_MANUAL)
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="marked_attendance_records",
    )
    marked_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["student__username"]
        constraints = [
            models.UniqueConstraint(fields=["session", "student"], name="unique_attendance_record")
        ]

    def clean(self):
        if getattr(self.student, "role", None) != "student":
            raise ValidationError("Only student users can have attendance records.")

    def __str__(self) -> str:
        return f"{self.student.display_name} - {self.get_status_display()}"
