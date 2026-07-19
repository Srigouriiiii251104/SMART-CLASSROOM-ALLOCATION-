from django.urls import path

from .api import MarkAttendanceAPIView, GenerateQRAttendanceAPIView
from .views import (
    AttendanceSessionCreateView,
    AttendanceSessionDetailView,
    AttendanceSessionListView,
    QRAnalyticsView,
    mark_attendance_manual,
)


app_name = "attendance"

urlpatterns = [
    path("", AttendanceSessionListView.as_view(), name="session_list"),
    path("sessions/add/", AttendanceSessionCreateView.as_view(), name="session_add"),
    path("sessions/<int:pk>/", AttendanceSessionDetailView.as_view(), name="session_detail"),
    path("sessions/<int:session_pk>/mark-student/<int:student_pk>/", mark_attendance_manual, name="mark_manual"),
    path("api/mark/", MarkAttendanceAPIView.as_view(), name="api_mark"),
    path("api/generate_qr/", GenerateQRAttendanceAPIView.as_view(), name="api_generate_qr"),
    path("analytics/qr/", QRAnalyticsView.as_view(), name="qr_analytics"),
]
