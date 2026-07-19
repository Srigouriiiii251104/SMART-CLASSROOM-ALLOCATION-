from rest_framework import serializers

from .models import ExamHallAllocation, ExamSchedule, SeatingAssignment


class ExamScheduleSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source="offering.course.code", read_only=True)

    class Meta:
        model = ExamSchedule
        fields = [
            "id",
            "title",
            "course_code",
            "exam_date",
            "start_time",
            "end_time",
            "exam_type",
            "status",
        ]


class ExamHallAllocationSerializer(serializers.ModelSerializer):
    hall_name = serializers.CharField(source="classroom.name", read_only=True)

    class Meta:
        model = ExamHallAllocation
        fields = ["id", "hall_name", "allocated_students"]


class SeatingAssignmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.display_name", read_only=True)
    hall_name = serializers.CharField(source="classroom.name", read_only=True)

    class Meta:
        model = SeatingAssignment
        fields = ["student_name", "hall_name", "seat_number"]
