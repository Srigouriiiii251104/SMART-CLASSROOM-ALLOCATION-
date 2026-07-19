from collections import Counter

from academics.models import Classroom, Term, TimetableEntry
from attendance.models import AttendanceRecord, AttendanceSession
from exams.models import ExamSchedule
from notifications_app.models import Notification
from resources.models import ResourceBooking


DAY_LABELS = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
}


def _base_timetable_for_user(user):
    active_term = Term.objects.filter(is_active=True).first()
    if not active_term:
        return TimetableEntry.objects.none()
    queryset = TimetableEntry.objects.filter(offering__term=active_term).select_related(
        "offering__course",
        "offering__faculty",
        "classroom",
        "timeslot",
    )
    if user.role == "faculty":
        queryset = queryset.filter(offering__faculty=user)
    elif user.role == "student":
        queryset = queryset.filter(offering__enrollments__student=user).distinct()
    return queryset


def build_dashboard_metrics(user):
    timetable_entries = _base_timetable_for_user(user)
    classrooms = Classroom.objects.all()
    attendance_records = AttendanceRecord.objects.all()
    if user.role == "student":
        attendance_records = attendance_records.filter(student=user)
    elif user.role == "faculty":
        attendance_records = attendance_records.filter(session__timetable_entry__offering__faculty=user)

    room_usage_counts = Counter(timetable_entries.values_list("classroom__name", flat=True))
    day_usage_counts = Counter(timetable_entries.values_list("timeslot__day_of_week", flat=True))
    resource_bookings = ResourceBooking.objects.all()
    if user.role == "student":
        resource_bookings = resource_bookings.filter(requested_by=user)

    attendance_trends = (
        attendance_records.values("session__session_date")
        .order_by("-session__session_date")[:7]
    )

    resource_categories = list(
        ResourceBooking.objects.values_list("resource__category__name", flat=True).distinct()
    )
    resource_utilization_data = [
        ResourceBooking.objects.filter(resource__category__name=name).count()
        for name in resource_categories
    ]

    faculty_load_map = (
        TimetableEntry.objects.filter(offering__term__is_active=True)
        .values_list("offering__faculty__first_name", "offering__faculty__last_name")
    )
    faculty_counter = Counter(
        (" ".join(filter(None, names)).strip() or "Faculty") for names in faculty_load_map
    )

    return {
        "cards": {
            "classrooms_total": classrooms.count(),
            "classrooms_available": classrooms.filter(status=Classroom.STATUS_AVAILABLE).count(),
            "scheduled_sessions": timetable_entries.count(),
            "resource_bookings": resource_bookings.count(),
            "attendance_rate": round(
                attendance_records.filter(status=AttendanceRecord.STATUS_PRESENT).count()
                / max(attendance_records.count(), 1)
                * 100,
                1,
            ),
            "exam_halls": ExamSchedule.objects.filter(status=ExamSchedule.STATUS_SCHEDULED).count(),
        },
        "charts": {
            "room_occupancy": {
                "labels": list(room_usage_counts.keys()),
                "data": list(room_usage_counts.values()),
            },
            "attendance_trends": {
                "labels": [item["session__session_date"].strftime("%d %b") for item in attendance_trends],
                "data": [attendance_records.filter(session__session_date=item["session__session_date"]).count() for item in attendance_trends],
            },
            "resource_utilization": {
                "labels": resource_categories,
                "data": resource_utilization_data,
            },
            "faculty_workload": {
                "labels": list(faculty_counter.keys())[:5],
                "data": list(faculty_counter.values())[:5],
            },
            "peak_usage": {
                "labels": [DAY_LABELS.get(day, str(day)) for day in day_usage_counts.keys()],
                "data": list(day_usage_counts.values()),
            },
        },
    }


def build_dashboard_context(user):
    metrics = build_dashboard_metrics(user)
    timetable_entries = _base_timetable_for_user(user)[:8]
    notifications = Notification.objects.filter(recipient=user)[:6]
    exams = ExamSchedule.objects.filter(status=ExamSchedule.STATUS_SCHEDULED).select_related("offering__course")
    attendance_sessions = AttendanceSession.objects.select_related(
        "timetable_entry__offering__course",
        "timetable_entry__offering__faculty",
    )

    if user.role == "faculty":
        exams = exams.filter(offering__faculty=user)
        attendance_sessions = attendance_sessions.filter(timetable_entry__offering__faculty=user)
    elif user.role == "student":
        exams = exams.filter(offering__enrollments__student=user).distinct()
        attendance_sessions = attendance_sessions.filter(
            timetable_entry__offering__enrollments__student=user
        ).distinct()

    return {
        "dashboard_metrics": metrics,
        "timetable_entries": timetable_entries,
        "notifications": notifications,
        "exam_schedules": exams[:5],
        "attendance_sessions": attendance_sessions[:5],
    }
