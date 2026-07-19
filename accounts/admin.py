from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import FacultyProfile, StudentProfile, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "role", "is_active")
    list_filter = ("role", "is_active", "is_staff")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Smart Classroom", {"fields": ("role", "phone_number")}),
    )


@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
    list_display = ("employee_id", "user", "department", "designation")
    search_fields = ("employee_id", "user__username", "user__first_name", "user__last_name")
    list_filter = ("department",)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("student_id", "user", "program", "semester", "section")
    search_fields = ("student_id", "user__username", "user__first_name", "user__last_name")
    list_filter = ("program", "semester", "section")
