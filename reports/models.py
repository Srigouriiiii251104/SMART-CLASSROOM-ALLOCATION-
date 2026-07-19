from django.conf import settings
from django.db import models


class GeneratedReport(models.Model):
    TYPE_TIMETABLE = "timetable"
    TYPE_ATTENDANCE = "attendance"
    TYPE_EXAM = "exam"
    TYPE_RESOURCE = "resource"

    TYPE_CHOICES = [
        (TYPE_TIMETABLE, "Timetable"),
        (TYPE_ATTENDANCE, "Attendance"),
        (TYPE_EXAM, "Exam Seating"),
        (TYPE_RESOURCE, "Resource Usage"),
    ]

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_reports",
    )
    report_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    filters = models.JSONField(default=dict, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-generated_at"]

    def __str__(self) -> str:
        return f"{self.report_type} @ {self.generated_at:%Y-%m-%d %H:%M}"
