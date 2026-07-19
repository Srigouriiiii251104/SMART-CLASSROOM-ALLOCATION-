from django.core.exceptions import ValidationError
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User

from .models import Classroom, Term, TimeSlot, TimetableEntry
from .serializers import ClassroomSerializer, TimetableEntrySerializer
from .services import generate_timetable, list_available_classrooms, move_timetable_entry


class AdminOrFacultyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in {User.ROLE_ADMIN, User.ROLE_FACULTY}


class TimetableEntryListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        term_id = request.query_params.get("term")
        entries = TimetableEntry.objects.select_related(
            "offering__course",
            "offering__faculty",
            "classroom",
            "timeslot",
        )
        if term_id:
            entries = entries.filter(offering__term_id=term_id)
        serializer = TimetableEntrySerializer(entries, many=True)
        return Response(serializer.data)


class TimetableGenerateAPIView(APIView):
    permission_classes = [AdminOrFacultyPermission]

    def post(self, request):
        term = None
        term_id = request.data.get("term_id")
        if term_id:
            term = Term.objects.filter(pk=term_id).first()
        try:
            result = generate_timetable(term)
        except ValidationError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_201_CREATED)


class TimetableMoveAPIView(APIView):
    permission_classes = [AdminOrFacultyPermission]

    def post(self, request):
        try:
            entry = TimetableEntry.objects.select_related("offering").get(pk=request.data["entry_id"])
            classroom = Classroom.objects.get(pk=request.data["classroom_id"])
            timeslot = TimeSlot.objects.get(pk=request.data["timeslot_id"])
            move_timetable_entry(entry, classroom, timeslot)
        except (KeyError, TimetableEntry.DoesNotExist, Classroom.DoesNotExist, TimeSlot.DoesNotExist):
            return Response({"detail": "Invalid timetable move request."}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(TimetableEntrySerializer(entry).data)


class FreeClassroomAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        timeslot_id = request.query_params.get("timeslot_id")
        if not timeslot_id:
            return Response({"detail": "timeslot_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            timeslot = TimeSlot.objects.get(pk=timeslot_id)
        except TimeSlot.DoesNotExist:
            return Response({"detail": "Time slot not found."}, status=status.HTTP_404_NOT_FOUND)

        queryset = list_available_classrooms(
            timeslot=timeslot,
            min_capacity=int(request.query_params.get("min_capacity", 0)),
            needs_smart=request.query_params.get("needs_smart") == "true",
            requires_lab=request.query_params.get("requires_lab") == "true",
        )
        return Response(ClassroomSerializer(queryset, many=True).data)
