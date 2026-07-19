from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .services import (
    build_attendance_report,
    build_exam_report,
    build_resource_report,
    build_timetable_report,
)


class ReportHubView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/reports.html"


@login_required
def timetable_report_view(request):
    return build_timetable_report(request.user)


@login_required
def attendance_report_view(request):
    return build_attendance_report(request.user, request.GET.get("session_id"))


@login_required
def exam_report_view(request):
    return build_exam_report(request.user, request.GET.get("exam_id"))


@login_required
def resource_report_view(request):
    return build_resource_report(request.user)
