from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class ExamSchedule(models.Model):
    TYPE_INTERNAL = "internal"
    TYPE_SEMESTER = "semester"
    TYPE_PRACTICAL = "practical"

    TYPE_CHOICES = [
        (TYPE_INTERNAL, "Internal"),
        (TYPE_SEMESTER, "Semester"),
        (TYPE_PRACTICAL, "Practical"),
    ]

    STATUS_DRAFT = "draft"
    STATUS_SCHEDULED = "scheduled"
    STATUS_COMPLETED = "completed"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_COMPLETED, "Completed"),
    ]

    offering = models.ForeignKey("academics.CourseOffering", on_delete=models.CASCADE, related_name="exams")
    title = models.CharField(max_length=150)
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    exam_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_INTERNAL)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["exam_date", "start_time"]

    @property
    def expected_students(self) -> int:
        return self.offering.enrollments.filter(status="active").count()

    def __str__(self) -> str:
        return f"{self.title} - {self.offering.course.code}"


class ExamHallAllocation(models.Model):
    exam = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE, related_name="hall_allocations")
    classroom = models.ForeignKey("academics.Classroom", on_delete=models.CASCADE, related_name="exam_allocations")
    allocated_students = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["classroom__name"]
        constraints = [
            models.UniqueConstraint(fields=["exam", "classroom"], name="unique_exam_hall"),
        ]

    def clean(self):
        if not self.classroom.is_exam_hall:
            raise ValidationError("Only classrooms marked as exam halls can be allocated.")
        overlapping = ExamHallAllocation.objects.filter(
            classroom=self.classroom,
            exam__exam_date=self.exam.exam_date,
            exam__start_time__lt=self.exam.end_time,
            exam__end_time__gt=self.exam.start_time,
        ).exclude(pk=self.pk)
        if overlapping.exists():
            raise ValidationError("This hall is already allocated for another exam in the same time window.")

    def __str__(self) -> str:
        return f"{self.classroom.name} -> {self.exam.title}"


class InvigilatorAssignment(models.Model):
    exam = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE, related_name="invigilator_assignments")
    faculty = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="invigilations")
    classroom = models.ForeignKey("academics.Classroom", on_delete=models.CASCADE, related_name="invigilators")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["exam", "faculty", "classroom"], name="unique_invigilator_exam_hall"),
        ]

    def clean(self):
        if getattr(self.faculty, "role", None) != "faculty":
            raise ValidationError("Only faculty users can be assigned as invigilators.")

    def __str__(self) -> str:
        return f"{self.faculty.display_name} - {self.classroom.name}"


class SeatingAssignment(models.Model):
    exam = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE, related_name="seating_assignments")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="seating_assignments")
    classroom = models.ForeignKey("academics.Classroom", on_delete=models.CASCADE, related_name="seating_assignments")
    seat_number = models.CharField(max_length=20)

    class Meta:
        ordering = ["classroom__name", "seat_number"]
        constraints = [
            models.UniqueConstraint(fields=["exam", "student"], name="unique_student_exam_seat"),
            models.UniqueConstraint(fields=["exam", "classroom", "seat_number"], name="unique_exam_classroom_seat"),
        ]

    def __str__(self) -> str:
        return f"{self.student.display_name} - {self.seat_number}"
