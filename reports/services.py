from io import BytesIO

from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from academics.models import Term, TimetableEntry
from attendance.models import AttendanceSession
from exams.models import ExamSchedule
from resources.models import ResourceBooking

from .models import GeneratedReport


def _pdf_response(filename: str, title: str, lines: list[str]):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 20 * mm
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(20 * mm, y, title)
    y -= 10 * mm
    pdf.setFont("Helvetica", 10)
    for line in lines:
        if y < 20 * mm:
            pdf.showPage()
            y = height - 20 * mm
            pdf.setFont("Helvetica", 10)
        pdf.drawString(20 * mm, y, line[:110])
        y -= 7 * mm
    pdf.save()
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def build_timetable_report(user):
    term = Term.objects.filter(is_active=True).first()
    entries = TimetableEntry.objects.filter(offering__term=term).select_related(
        "offering__course",
        "offering__faculty",
        "classroom",
        "timeslot",
    )
    if user.role == "faculty":
        entries = entries.filter(offering__faculty=user)
    elif user.role == "student":
        entries = entries.filter(offering__enrollments__student=user).distinct()

    lines = [
        f"{entry.offering.course.code} | {entry.timeslot} | {entry.classroom.name if entry.classroom else 'TBA'} | {entry.offering.faculty.display_name}"
        for entry in entries
    ]
    GeneratedReport.objects.create(requested_by=user, report_type=GeneratedReport.TYPE_TIMETABLE, filters={"term": term.name if term else "N/A"})
    return _pdf_response("timetable-report.pdf", "Timetable Report", lines or ["No timetable entries found."])


def build_attendance_report(user, session_id=None):
    sessions = AttendanceSession.objects.select_related("timetable_entry__offering__course")
    if session_id:
        sessions = sessions.filter(pk=session_id)
    lines = []
    for session in sessions:
        for record in session.records.select_related("student"):
            lines.append(
                f"{session.timetable_entry.offering.course.code} | {session.session_date} | {record.student.display_name} | {record.get_status_display()}"
            )
    GeneratedReport.objects.create(requested_by=user, report_type=GeneratedReport.TYPE_ATTENDANCE, filters={"session_id": session_id})
    return _pdf_response("attendance-report.pdf", "Attendance Report", lines or ["No attendance records found."])


def build_exam_report(user, exam_id=None):
    exams = ExamSchedule.objects.select_related("offering__course")
    if exam_id:
        exams = exams.filter(pk=exam_id)
    lines = []
    for exam in exams:
        for seat in exam.seating_assignments.select_related("student", "classroom"):
            lines.append(
                f"{exam.title} | {seat.student.display_name} | {seat.classroom.name} | {seat.seat_number}"
            )
    GeneratedReport.objects.create(requested_by=user, report_type=GeneratedReport.TYPE_EXAM, filters={"exam_id": exam_id})
    return _pdf_response("exam-seating-report.pdf", "Exam Seating Report", lines or ["No seating assignments found."])


def build_resource_report(user):
    bookings = ResourceBooking.objects.select_related("resource", "requested_by")
    lines = [
        f"{booking.resource.name} | {booking.booking_date} | {booking.requested_by.display_name} | {booking.get_status_display()}"
        for booking in bookings
    ]
    GeneratedReport.objects.create(requested_by=user, report_type=GeneratedReport.TYPE_RESOURCE, filters={})
    return _pdf_response("resource-usage-report.pdf", "Resource Usage Report", lines or ["No resource activity found."])
