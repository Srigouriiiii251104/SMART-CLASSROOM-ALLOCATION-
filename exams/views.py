from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView

from accounts.models import User
from .forms import ExamScheduleForm
from .models import ExamSchedule
from .services import allocate_exam_halls


class ExamScheduleListView(LoginRequiredMixin, ListView):
    model = ExamSchedule
    template_name = "exams/exam_list.html"
    context_object_name = "exams"

    def get_queryset(self):
        qs = ExamSchedule.objects.select_related("offering__course")
        if self.request.user.role == User.ROLE_STUDENT:
            qs = qs.filter(offering__enrollments__student=self.request.user).distinct()
        elif self.request.user.role == User.ROLE_FACULTY:
            qs = qs.filter(offering__faculty=self.request.user).distinct()
        return qs


class ExamScheduleCreateView(LoginRequiredMixin, CreateView):
    model = ExamSchedule
    form_class = ExamScheduleForm
    template_name = "shared/form.html"
    success_url = reverse_lazy("exams:exam_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Schedule Exam"
        return context


class ExamScheduleDetailView(LoginRequiredMixin, DetailView):
    model = ExamSchedule
    template_name = "exams/exam_detail.html"
    context_object_name = "exam"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.role == User.ROLE_STUDENT:
            context["my_seat"] = self.object.seating_assignments.filter(student=self.request.user).first()
        return context


class AllocateExamView(LoginRequiredMixin, View):
    def post(self, request, pk):
        exam = get_object_or_404(ExamSchedule, pk=pk)
        result = allocate_exam_halls(exam)
        if result["allocated"]:
            messages.success(request, result["message"])
        else:
            messages.error(request, result["message"])
        return redirect("exams:exam_detail", pk=pk)


class ExamAllocationAPIView(LoginRequiredMixin, View):
    def post(self, request, pk):
        exam = get_object_or_404(ExamSchedule, pk=pk)
        result = allocate_exam_halls(exam)
        return JsonResponse(result)
