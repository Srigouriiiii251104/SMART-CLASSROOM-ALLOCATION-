from rest_framework import serializers

from .models import AttendanceRecord, AttendanceSession


class AttendanceSessionSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source="timetable_entry.offering.course.code", read_only=True)

    class Meta:
        model = AttendanceSession
        fields = ["id", "course_code", "session_date", "allow_manual", "allow_qr", "face_recognition_enabled", "qr_token"]


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.display_name", read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = ["id", "session", "student", "student_name", "status", "access_method", "marked_at"]
