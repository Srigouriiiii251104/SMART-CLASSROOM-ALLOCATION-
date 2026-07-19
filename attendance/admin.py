from django.contrib import admin

from .models import AttendanceRecord, AttendanceSession


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ("timetable_entry", "session_date", "allow_qr", "face_recognition_enabled")
    list_filter = ("session_date", "allow_qr", "face_recognition_enabled")


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ("session", "student", "status", "access_method", "marked_at")
    list_filter = ("status", "access_method", "session__session_date")
