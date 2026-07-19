import io
import uuid

import qrcode
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models


class Department(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class Program(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="programs")
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=120)
    duration_semesters = models.PositiveSmallIntegerField(default=4)

    class Meta:
        ordering = ["department__name", "name"]

    def __str__(self) -> str:
        return self.name


class Term(models.Model):
    name = models.CharField(max_length=50, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_active:
            Term.objects.exclude(pk=self.pk).update(is_active=False)

    def __str__(self) -> str:
        return self.name


class Classroom(models.Model):
    STATUS_AVAILABLE = "available"
    STATUS_MAINTENANCE = "maintenance"
    STATUS_INACTIVE = "inactive"

    STATUS_CHOICES = [
        (STATUS_AVAILABLE, "Available"),
        (STATUS_MAINTENANCE, "Maintenance"),
        (STATUS_INACTIVE, "Inactive"),
    ]

    name = models.CharField(max_length=80, unique=True)
    building = models.CharField(max_length=80)
    floor = models.CharField(max_length=30, blank=True)
    capacity = models.PositiveIntegerField()
    is_smart = models.BooleanField(default=False)
    has_projector = models.BooleanField(default=False)
    has_computers = models.BooleanField(default=False)
    is_exam_hall = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    notes = models.TextField(blank=True)
    qr_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    qr_image = models.ImageField(upload_to="qr/classrooms/", blank=True)

    class Meta:
        ordering = ["building", "name"]

    def save(self, *args, **kwargs):
        update_fields = kwargs.get("update_fields")
        generating_only = update_fields and "qr_image" in update_fields and len(update_fields) == 1
        super().save(*args, **kwargs)
        if not self.qr_image and not generating_only:
            self._generate_qr_code()

    def _generate_qr_code(self):
        payload = f"classroom:{self.pk}:{self.qr_token}"
        image = qrcode.make(payload)
        stream = io.BytesIO()
        image.save(stream, format="PNG")
        self.qr_image.save(
            f"classroom-{self.pk}.png",
            ContentFile(stream.getvalue()),
            save=False,
        )
        super().save(update_fields=["qr_image"])

    @property
    def feature_summary(self) -> str:
        features = []
        if self.is_smart:
            features.append("Smart")
        if self.has_projector:
            features.append("Projector")
        if self.has_computers:
            features.append("Computer Lab")
        return ", ".join(features) or "Standard"

    def __str__(self) -> str:
        return f"{self.name} ({self.building})"


class TimeSlot(models.Model):
    DAY_CHOICES = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]

    day_of_week = models.PositiveSmallIntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    label = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["day_of_week", "start_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["day_of_week", "start_time", "end_time"],
                name="unique_day_time_slot",
            )
        ]

    def __str__(self) -> str:
        return f"{self.get_day_of_week_display()} {self.start_time:%H:%M}-{self.end_time:%H:%M}"


class Course(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="courses")
    program = models.ForeignKey(
        Program,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses",
    )
    code = models.CharField(max_length=30, unique=True)
    title = models.CharField(max_length=150)
    credit_hours = models.PositiveSmallIntegerField(default=3)
    requires_lab = models.BooleanField(default=False)
    smart_classroom_needed = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["code"]

    def __str__(self) -> str:
        return f"{self.code} - {self.title}"


class CourseOffering(models.Model):
    DELIVERY_PHYSICAL = "physical"
    DELIVERY_HYBRID = "hybrid"

    DELIVERY_CHOICES = [
        (DELIVERY_PHYSICAL, "Physical"),
        (DELIVERY_HYBRID, "Hybrid"),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="offerings")
    faculty = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teaching_assignments",
    )
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="offerings")
    section = models.CharField(max_length=20, default="A")
    student_count = models.PositiveIntegerField(default=0)
    sessions_per_week = models.PositiveSmallIntegerField(default=3)
    preferred_building = models.CharField(max_length=80, blank=True)
    resource_requirements = models.JSONField(default=list, blank=True)
    delivery_mode = models.CharField(
        max_length=20,
        choices=DELIVERY_CHOICES,
        default=DELIVERY_PHYSICAL,
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["course__code", "section"]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "faculty", "term", "section"],
                name="unique_offering_per_term",
            )
        ]

    def clean(self):
        if self.faculty and getattr(self.faculty, "role", None) != "faculty":
            raise ValidationError("Only faculty users can be assigned to course offerings.")

    def __str__(self) -> str:
        return f"{self.course.code} / {self.section}"


class Enrollment(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_DROPPED = "dropped"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_DROPPED, "Dropped"),
    ]

    offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name="enrollments")
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_enrollments",
    )
    enrolled_on = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    class Meta:
        ordering = ["student__username"]
        constraints = [
            models.UniqueConstraint(
                fields=["offering", "student"],
                name="unique_student_offering_enrollment",
            )
        ]

    def clean(self):
        if self.student and getattr(self.student, "role", None) != "student":
            raise ValidationError("Only student users can be enrolled in offerings.")

    def __str__(self) -> str:
        return f"{self.student.display_name} -> {self.offering}"


class TimetableEntry(models.Model):
    TYPE_LECTURE = "lecture"
    TYPE_LAB = "lab"
    TYPE_TUTORIAL = "tutorial"
    TYPE_EXAM = "exam"

    SESSION_TYPE_CHOICES = [
        (TYPE_LECTURE, "Lecture"),
        (TYPE_LAB, "Lab"),
        (TYPE_TUTORIAL, "Tutorial"),
        (TYPE_EXAM, "Exam"),
    ]

    offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name="timetable_entries")
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="timetable_entries",
    )
    timeslot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name="timetable_entries")
    session_type = models.CharField(
        max_length=20,
        choices=SESSION_TYPE_CHOICES,
        default=TYPE_LECTURE,
    )
    notes = models.TextField(blank=True)
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timeslot__day_of_week", "timeslot__start_time", "offering__course__code"]
        constraints = [
            models.UniqueConstraint(
                fields=["offering", "timeslot"],
                name="unique_offering_timeslot",
            ),
            models.UniqueConstraint(
                fields=["classroom", "timeslot"],
                name="unique_classroom_timeslot",
            ),
        ]

    def clean(self):
        conflicts = TimetableEntry.objects.filter(timeslot=self.timeslot).exclude(pk=self.pk)
        if self.classroom and conflicts.filter(classroom=self.classroom).exists():
            raise ValidationError({"classroom": "This classroom is already booked for the selected time slot."})
        if conflicts.filter(offering__faculty=self.offering.faculty).exists():
            raise ValidationError("Faculty overlap detected for the selected time slot.")

    def __str__(self) -> str:
        room_name = self.classroom.name if self.classroom else "Unassigned"
        return f"{self.offering} - {self.timeslot} - {room_name}"
