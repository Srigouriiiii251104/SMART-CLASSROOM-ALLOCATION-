from rest_framework import serializers

from .models import Classroom, TimeSlot, TimetableEntry


class ClassroomSerializer(serializers.ModelSerializer):
    feature_summary = serializers.ReadOnlyField()

    class Meta:
        model = Classroom
        fields = [
            "id",
            "name",
            "building",
            "floor",
            "capacity",
            "is_smart",
            "has_projector",
            "has_computers",
            "is_exam_hall",
            "status",
            "feature_summary",
        ]


class TimeSlotSerializer(serializers.ModelSerializer):
    display = serializers.SerializerMethodField()

    def get_display(self, obj):
        return str(obj)

    class Meta:
        model = TimeSlot
        fields = ["id", "day_of_week", "start_time", "end_time", "label", "display"]


class TimetableEntrySerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source="offering.course.code", read_only=True)
    course_title = serializers.CharField(source="offering.course.title", read_only=True)
    faculty_name = serializers.CharField(source="offering.faculty.display_name", read_only=True)
    classroom_name = serializers.CharField(source="classroom.name", read_only=True)
    timeslot_display = serializers.SerializerMethodField()

    def get_timeslot_display(self, obj):
        return str(obj.timeslot)

    class Meta:
        model = TimetableEntry
        fields = [
            "id",
            "course_code",
            "course_title",
            "faculty_name",
            "classroom",
            "classroom_name",
            "timeslot",
            "timeslot_display",
            "session_type",
            "is_locked",
        ]
