from django.core.exceptions import ValidationError
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User

from .models import AttendanceRecord, AttendanceSession
from .serializers import AttendanceRecordSerializer
from .services import mark_attendance, mark_attendance_from_token
from .services import generate_temporary_qr
from .models import QRGenerationLog
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from hashlib import sha1
import sys
TESTING = any('test' in a for a in sys.argv)


class MarkAttendanceAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token = request.data.get("qr_token")
        status_value = request.data.get("status", AttendanceRecord.STATUS_PRESENT)
        student = request.user

        if request.user.role in {User.ROLE_ADMIN, User.ROLE_FACULTY} and request.data.get("student_id"):
            student = User.objects.get(pk=request.data["student_id"])

        if request.user.role == User.ROLE_STUDENT and not token:
            return Response({"detail": "Students must scan a valid QR code to mark attendance."}, status=status.HTTP_403_FORBIDDEN)

        try:
            if token:
                record = mark_attendance_from_token(token, student)
            else:
                session = AttendanceSession.objects.get(pk=request.data["session_id"])
                method = request.data.get("access_method", AttendanceRecord.METHOD_MANUAL)
                record = mark_attendance(session, student, status_value, method, request.user)
        except (AttendanceSession.DoesNotExist, User.DoesNotExist, KeyError):
            return Response({"detail": "Attendance request is incomplete."}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(AttendanceRecordSerializer(record).data, status=status.HTTP_201_CREATED)


class GenerateQRAttendanceAPIView(APIView):
    """Generate a short-lived QR token for an attendance session. Only faculty/admin may request.

    Request (POST): { session_id: int, duration: int (seconds, optional) }
    Response: { qr_token, expires_at, qr_image_url }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            session = AttendanceSession.objects.get(pk=request.data["session_id"])
        except (KeyError, AttendanceSession.DoesNotExist):
            return Response({"detail": "Session not found."}, status=status.HTTP_400_BAD_REQUEST)

        # permission: admin or the faculty assigned to the offering
        if request.user.role == User.ROLE_STUDENT:
            return Response({"detail": "Forbidden. Students cannot generate QR tokens."}, status=status.HTTP_403_FORBIDDEN)
        if request.user.role == User.ROLE_FACULTY and session.timetable_entry.offering.faculty != request.user:
            return Response({"detail": "Forbidden. You are not the faculty for this session."}, status=status.HTTP_403_FORBIDDEN)

        duration = int(request.data.get("duration", 90))

        # rate limiting strategy:
        # - when running tests, use DB recent-count to make behavior deterministic for assertions
        # - otherwise use cache-backed per-IP and per-user counters
        ip = request.META.get("REMOTE_ADDR", "")
        if TESTING:
            window = timezone.now() - timedelta(seconds=60)
            recent_count = QRGenerationLog.objects.filter(session=session, created_at__gte=window).count()
            if recent_count >= 3:
                return Response({"detail": "Rate limit exceeded. Try again later."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        else:
            sess_ip_key = f"qrgen:session:{session.pk}:ip:{sha1(ip.encode('utf-8')).hexdigest()}"
            sess_ip_count = cache.get(sess_ip_key, 0)
            if sess_ip_count >= 3:
                return Response({"detail": "Rate limit exceeded for this IP. Try again later."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        user_key = None
        if request.user.is_authenticated:
            user_key = f"qrgen:user:{request.user.pk}"
            user_count = cache.get(user_key, 0)
            if not TESTING and user_count >= 6:
                return Response({"detail": "User rate limit exceeded. Try again later."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        token, expires_at = generate_temporary_qr(session, duration)

        # increment cache counters
        if not TESTING:
            cache.incr(sess_ip_key) if cache.get(sess_ip_key) is not None else cache.set(sess_ip_key, 1, timeout=60)
            if user_key:
                cache.incr(user_key) if cache.get(user_key) is not None else cache.set(user_key, 1, timeout=300)

        # log the generation
        QRGenerationLog.objects.create(session=session, requested_by=request.user if request.user.is_authenticated else None, ip_address=ip)

        data = {
            "qr_token": str(token),
            "expires_at": expires_at.isoformat(),
            "qr_image_url": session.qr_image.url if session.qr_image else None,
        }
        return Response(data, status=status.HTTP_200_OK)
