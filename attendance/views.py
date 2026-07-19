from django.db.models import Count, Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView, ListView

from academics.models import Enrollment

from .forms import AttendanceSessionForm
from .models import AttendanceRecord, AttendanceSession
from .models import QRGenerationLog
from django.views.generic import TemplateView
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .services import mark_attendance
from accounts.models import User
import csv
from django.utils.dateparse import parse_date
from django.utils import timezone
from datetime import datetime


class AttendanceSessionListView(LoginRequiredMixin, ListView):
    model = AttendanceSession
    template_name = "attendance/session_list.html"
    context_object_name = "sessions"

    def get_queryset(self):
        queryset = AttendanceSession.objects.select_related(
            "timetable_entry__offering__course",
            "timetable_entry__offering__faculty",
            "timetable_entry__classroom",
            "timetable_entry__timeslot",
        ).annotate(
            recorded_count=Count("records", distinct=True),
            present_count=Count(
                "records",
                filter=Q(records__status=AttendanceRecord.STATUS_PRESENT),
                distinct=True,
            ),
            enrolled_count=Count(
                "timetable_entry__offering__enrollments",
                filter=Q(timetable_entry__offering__enrollments__status=Enrollment.STATUS_ACTIVE),
                distinct=True,
            ),
        )
        if self.request.user.role == "student":
            queryset = queryset.filter(
                timetable_entry__offering__enrollments__student=self.request.user
            ).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sessions = list(context["sessions"])
        for session in sessions:
            session.pending_count = max(session.enrolled_count - session.recorded_count, 0)
            session.completion_rate = round((session.recorded_count / session.enrolled_count) * 100) if session.enrolled_count else 0

        context["session_counts"] = {
            "sessions": len(sessions),
            "records": sum(session.recorded_count for session in sessions),
            "pending": sum(session.pending_count for session in sessions),
        }
        context["sessions"] = sessions
        return context


class QRAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = "attendance/qr_analytics.html"

    def dispatch(self, request, *args, **kwargs):
        # only allow admins
        if not request.user.is_authenticated or request.user.role != "admin":
            return redirect("/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # parse optional date filters
        start = self.request.GET.get('start_date')
        end = self.request.GET.get('end_date')
        qs = QRGenerationLog.objects.all()
        if start:
            sd = parse_date(start)
            if sd:
                qs = qs.filter(created_at__date__gte=sd)
        if end:
            ed = parse_date(end)
            if ed:
                qs = qs.filter(created_at__date__lte=ed)

        # counts per day
        daily = (
            qs.annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )
        # top sessions by generations
        top_sessions = (
            QRGenerationLog.objects.values(
                "session__pk",
                "session__timetable_entry__offering__course__code",
            )
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )
        context["daily"] = list(daily)
        context["top_sessions"] = list(top_sessions)
        context['start_date'] = start or ''
        context['end_date'] = end or ''
        return context

    def post(self, request, *args, **kwargs):
        # handle CSV export
        action = request.POST.get('action')
        if action == 'export_csv':
            start = request.POST.get('start_date')
            end = request.POST.get('end_date')
            qs = QRGenerationLog.objects.all()
            if start:
                sd = parse_date(start)
                if sd:
                    qs = qs.filter(created_at__date__gte=sd)
            if end:
                ed = parse_date(end)
                if ed:
                    qs = qs.filter(created_at__date__lte=ed)

            # stream CSV
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="qr_generation_{timezone.now().date()}.csv"'
            writer = csv.writer(response)
            writer.writerow(['id', 'session_id', 'requested_by_id', 'ip_address', 'created_at'])
            for r in qs.order_by('created_at'):
                writer.writerow([r.id, r.session_id, r.requested_by_id if r.requested_by else '', r.ip_address, r.created_at.isoformat()])
            return response
        return super().get(request, *args, **kwargs)


class AttendanceSessionCreateView(LoginRequiredMixin, CreateView):
    model = AttendanceSession
    form_class = AttendanceSessionForm
    template_name = "shared/form.html"
    success_url = "/attendance/"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create Attendance Session"
        return context


class AttendanceSessionDetailView(LoginRequiredMixin, DetailView):
    model = AttendanceSession
    template_name = "attendance/session_detail.html"
    context_object_name = "session"

    def get_queryset(self):
        return AttendanceSession.objects.select_related(
            "timetable_entry__offering__course",
            "timetable_entry__offering__faculty",
            "timetable_entry__classroom",
            "timetable_entry__timeslot",
            "created_by",
        ).prefetch_related(
            "records__student__studentprofile",
            "timetable_entry__offering__enrollments__student__studentprofile",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = context["session"]
        enrollments = session.timetable_entry.offering.enrollments.filter(
            status=Enrollment.STATUS_ACTIVE
        ).select_related("student__studentprofile")
        record_map = {
            record.student_id: record
            for record in session.records.select_related("student__studentprofile")
        }
        roster_entries = []
        attendance_summary = {
            "total": 0,
            "present": 0,
            "late": 0,
            "absent": 0,
            "excused": 0,
            "pending": 0,
        }

        for enrollment in enrollments:
            student = enrollment.student
            profile = getattr(student, "studentprofile", None)
            record = record_map.get(student.id)
            status_key = record.status if record else "pending"
            attendance_summary["total"] += 1
            attendance_summary[status_key] += 1
            roster_entries.append(
                {
                    "student": student,
                    "profile": profile,
                    "record": record,
                    "status_key": status_key,
                    "status_label": record.get_status_display() if record else "Pending",
                    "method_label": record.get_access_method_display() if record else "Awaiting mark",
                }
            )

        marked_count = attendance_summary["total"] - attendance_summary["pending"]
        context["roster_entries"] = roster_entries
        context["attendance_summary"] = attendance_summary
        context["marked_count"] = marked_count
        context["completion_rate"] = round((marked_count / attendance_summary["total"]) * 100) if attendance_summary["total"] else 0
        return context


@login_required
@require_POST
def mark_attendance_manual(request, session_pk, student_pk):
    session = get_object_or_404(AttendanceSession, pk=session_pk)
    
    # Check permissions
    if request.user.role not in ['admin', 'faculty']:
        messages.error(request, "Permission denied.")
        return redirect('attendance:session_detail', pk=session_pk)
    if request.user.role == 'faculty' and session.timetable_entry.offering.faculty != request.user:
        messages.error(request, "Permission denied.")
        return redirect('attendance:session_detail', pk=session_pk)
        
    student = get_object_or_404(User, pk=student_pk)
    status_val = request.POST.get('status')
    
    if status_val == 'pending':
        AttendanceRecord.objects.filter(session=session, student=student).delete()
        messages.success(request, f"Cleared attendance record for {student.display_name}.")
    elif status_val in dict(AttendanceRecord.STATUS_CHOICES):
        mark_attendance(
            session=session,
            student=student,
            status=status_val,
            method=AttendanceRecord.METHOD_MANUAL,
            marked_by=request.user
        )
        messages.success(request, f"Updated attendance for {student.display_name} to {status_val.capitalize()}.")
    else:
        messages.error(request, "Invalid status value.")
        
    return redirect('attendance:session_detail', pk=session_pk)
