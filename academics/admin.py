from django.contrib import admin

from .models import (
    Classroom,
    Course,
    CourseOffering,
    Department,
    Enrollment,
    Program,
    Term,
    TimeSlot,
    TimetableEntry,
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "department", "duration_semesters")
    list_filter = ("department",)
    search_fields = ("code", "name")


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "is_active")
    list_filter = ("is_active",)


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ("name", "building", "capacity", "status", "is_smart", "is_exam_hall")
    list_filter = ("status", "is_smart", "is_exam_hall", "building")
    search_fields = ("name", "building")


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ("day_of_week", "start_time", "end_time", "label")
    list_filter = ("day_of_week",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "department", "credit_hours", "requires_lab")
    list_filter = ("department", "requires_lab", "smart_classroom_needed")
    search_fields = ("code", "title")


@admin.register(CourseOffering)
class CourseOfferingAdmin(admin.ModelAdmin):
    list_display = ("course", "faculty", "term", "section", "student_count", "sessions_per_week")
    list_filter = ("term", "course__department")
    search_fields = ("course__code", "course__title", "faculty__username")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("offering", "student", "status", "enrolled_on")
    list_filter = ("status", "offering__term")
    search_fields = ("student__username", "student__first_name", "student__last_name")


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ("offering", "classroom", "timeslot", "session_type", "is_locked")
    list_filter = ("session_type", "timeslot__day_of_week", "offering__term")
    search_fields = ("offering__course__code", "offering__course__title", "classroom__name")
