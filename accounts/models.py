from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    ROLE_ADMIN = "admin"
    ROLE_FACULTY = "faculty"
    ROLE_STUDENT = "student"

    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_FACULTY, "Faculty"),
        (ROLE_STUDENT, "Student"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    phone_number = models.CharField(max_length=20, blank=True)

    @property
    def display_name(self) -> str:
        return self.get_full_name() or self.username

    @property
    def is_faculty(self) -> bool:
        return self.role == self.ROLE_FACULTY

    @property
    def is_student(self) -> bool:
        return self.role == self.ROLE_STUDENT

    def __str__(self) -> str:
        return f"{self.display_name} ({self.get_role_display()})"


class FacultyProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=30, unique=True)
    department = models.ForeignKey(
        "academics.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="faculty_members",
    )
    designation = models.CharField(max_length=100, blank=True)
    specialization = models.CharField(max_length=150, blank=True)

    def clean(self):
        if self.user and self.user.role != User.ROLE_FACULTY:
            raise ValidationError("Faculty profiles can only be assigned to faculty users.")

    def __str__(self) -> str:
        return f"{self.employee_id} - {self.user.display_name}"


class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=30, unique=True)
    department = models.ForeignKey(
        "academics.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_members",
    )
    program = models.ForeignKey(
        "academics.Program",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
    )
    semester = models.PositiveSmallIntegerField(default=1)
    section = models.CharField(max_length=20, default="A")

    def clean(self):
        if self.user and self.user.role != User.ROLE_STUDENT:
            raise ValidationError("Student profiles can only be assigned to student users.")

    def __str__(self) -> str:
        return f"{self.student_id} - {self.user.display_name}"
