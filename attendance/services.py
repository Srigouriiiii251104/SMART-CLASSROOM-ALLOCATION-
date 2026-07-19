from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid

from academics.models import Enrollment

from .models import AttendanceRecord, AttendanceSession


def generate_temporary_qr(session: AttendanceSession, duration_seconds: int = 90):
    """Generate a new QR token for the given attendance session that expires after duration_seconds.

    Returns (token, expires_at).
    """
    token = uuid.uuid4()
    expires_at = timezone.now() + timezone.timedelta(seconds=duration_seconds)
    session.qr_token = token
    session.qr_expires_at = expires_at
    # regenerate QR image and save
    session._generate_qr_code()
    session.save()
    return token, expires_at


def mark_attendance(session: AttendanceSession, student, status: str, method: str, marked_by=None):
    is_enrolled = Enrollment.objects.filter(
        offering=session.timetable_entry.offering,
        student=student,
        status=Enrollment.STATUS_ACTIVE,
    ).exists()
    if not is_enrolled:
        raise ValidationError("Student is not enrolled in the selected course offering.")

    record, _ = AttendanceRecord.objects.update_or_create(
        session=session,
        student=student,
        defaults={"status": status, "access_method": method, "marked_by": marked_by},
    )
    return record


def mark_attendance_from_token(token: str, student):
    session = AttendanceSession.objects.filter(qr_token=token, allow_qr=True).first()
    if not session:
        raise ValidationError("Invalid or expired QR token.")

    # check if teacher has initiated QR session
    if not session.qr_expires_at:
        raise ValidationError("QR attendance has not been initiated by the teacher for this session.")

    # check expiry
    if timezone.now() > session.qr_expires_at:
        raise ValidationError("QR token has expired.")

    # mark attendance (idempotent)
    return mark_attendance(session, student, AttendanceRecord.STATUS_PRESENT, AttendanceRecord.METHOD_QR, student)
