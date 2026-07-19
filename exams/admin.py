from django.contrib import admin

from .models import ExamHallAllocation, ExamSchedule, InvigilatorAssignment, SeatingAssignment


@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ("title", "offering", "exam_date", "start_time", "end_time", "status")
    list_filter = ("status", "exam_type", "exam_date")
    search_fields = ("title", "offering__course__code", "offering__course__title")


@admin.register(ExamHallAllocation)
class ExamHallAllocationAdmin(admin.ModelAdmin):
    list_display = ("exam", "classroom", "allocated_students")


@admin.register(InvigilatorAssignment)
class InvigilatorAssignmentAdmin(admin.ModelAdmin):
    list_display = ("exam", "faculty", "classroom")


@admin.register(SeatingAssignment)
class SeatingAssignmentAdmin(admin.ModelAdmin):
    list_display = ("exam", "student", "classroom", "seat_number")
    search_fields = ("student__username", "student__first_name", "student__last_name")
