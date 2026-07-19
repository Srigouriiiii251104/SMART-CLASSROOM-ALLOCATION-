from django.urls import path

from .views import (
    ReportHubView,
    attendance_report_view,
    exam_report_view,
    resource_report_view,
    timetable_report_view,
)


app_name = "reports"

urlpatterns = [
    path("", ReportHubView.as_view(), name="hub"),
    path("timetable/", timetable_report_view, name="timetable"),
    path("attendance/", attendance_report_view, name="attendance"),
    path("exam/", exam_report_view, name="exam"),
    path("resource/", resource_report_view, name="resource"),
]
