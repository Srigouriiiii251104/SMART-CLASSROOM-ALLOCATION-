from django.utils import timezone

from academics.models import TimeSlot
from academics.services import list_available_classrooms
from attendance.models import AttendanceRecord
from resources.models import Resource

from .models import ChatbotInteraction


def _current_timeslot():
    now = timezone.localtime()
    return TimeSlot.objects.filter(
        day_of_week=now.weekday(),
        start_time__lte=now.time(),
        end_time__gte=now.time(),
    ).first()


def _free_classroom_reply():
    timeslot = _current_timeslot()
    if not timeslot:
        return "There is no active time slot right now. Open the timetable board to inspect the next available classroom window."

    classrooms = list_available_classrooms(timeslot)
    if not classrooms.exists():
        return f"No free classrooms are available for {timeslot}."
    names = ", ".join(classrooms.values_list("name", flat=True)[:6])
    return f"Free classrooms for {timeslot}: {names}."


def _timetable_reply(user):
    if user.role == "faculty":
        offerings = user.teaching_assignments.filter(term__is_active=True).prefetch_related("timetable_entries__classroom", "course")
        if not offerings.exists():
            return "No active timetable entries are assigned to you yet."
        offering = offerings.first()
        sessions = offering.timetable_entries.select_related("classroom", "timeslot")
        lines = [f"{entry.timeslot} in {entry.classroom.name if entry.classroom else 'TBA'}" for entry in sessions[:4]]
        return f"Your next timetable highlights for {offering.course.code}: " + "; ".join(lines)

    if user.role == "student":
        enrollments = user.course_enrollments.filter(offering__term__is_active=True).select_related("offering__course")
        if not enrollments.exists():
            return "You are not enrolled in any active offerings right now."
        offering = enrollments.first().offering
        sessions = offering.timetable_entries.select_related("classroom", "timeslot")
        lines = [f"{entry.timeslot} in {entry.classroom.name if entry.classroom else 'TBA'}" for entry in sessions[:4]]
        return f"Your timetable highlights for {offering.course.code}: " + "; ".join(lines)

    return "Admin users can review the complete timetable from the scheduling dashboard."


def _resource_reply():
    available = Resource.objects.filter(status=Resource.STATUS_AVAILABLE).count()
    maintenance = Resource.objects.filter(status=Resource.STATUS_MAINTENANCE).count()
    return f"There are {available} available resources and {maintenance} currently under maintenance."


def _attendance_reply(user):
    if user.role != "student":
        return "Attendance analytics are visible from the dashboard and report center."
    total = user.attendance_records.count()
    present = user.attendance_records.filter(status=AttendanceRecord.STATUS_PRESENT).count()
    rate = round((present / max(total, 1)) * 100, 1)
    return f"Your current attendance rate is {rate}% across {total} recorded sessions."


def respond_to_query(query: str, user):
    normalized = query.lower().strip()
    if "free classroom" in normalized or "available classroom" in normalized:
        response = _free_classroom_reply()
    elif "timetable" in normalized or "schedule" in normalized:
        response = _timetable_reply(user)
    elif "resource" in normalized or "projector" in normalized or "lab" in normalized:
        response = _resource_reply()
    elif "attendance" in normalized:
        response = _attendance_reply(user)
    else:
        response = (
            "I can help with free classrooms, timetable requests, attendance summaries, and resource availability. "
            "Try asking 'show free classrooms' or 'show my timetable'."
        )

    ChatbotInteraction.objects.create(user=user, query=query, response=response)
    return response
