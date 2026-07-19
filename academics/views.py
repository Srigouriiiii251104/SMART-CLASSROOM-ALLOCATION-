from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from accounts.mixins import RoleRequiredMixin
from accounts.models import User

from .forms import ClassroomForm
from .models import Classroom, Term, TimeSlot, TimetableEntry
from .services import detect_timetable_conflicts, generate_timetable


class ClassroomListView(LoginRequiredMixin, ListView):
    model = Classroom
    template_name = "academics/classroom_list.html"
    context_object_name = "classrooms"


class ClassroomCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    allowed_roles = (User.ROLE_ADMIN,)
    model = Classroom
    form_class = ClassroomForm
    template_name = "shared/form.html"
    success_url = reverse_lazy("academics:classroom_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add Classroom"
        return context


class ClassroomUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    allowed_roles = (User.ROLE_ADMIN,)
    model = Classroom
    form_class = ClassroomForm
    template_name = "shared/form.html"
    success_url = reverse_lazy("academics:classroom_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Edit Classroom"
        return context


class ClassroomDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    allowed_roles = (User.ROLE_ADMIN,)
    model = Classroom
    template_name = "shared/confirm_delete.html"
    success_url = reverse_lazy("academics:classroom_list")


class TimetableBoardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/timetable.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        term = Term.objects.filter(is_active=True).first()
        entries = TimetableEntry.objects.none()
        focus_entries = TimetableEntry.objects.none()
        cell_entries = {}
        classrooms = list(Classroom.objects.filter(status=Classroom.STATUS_AVAILABLE))
        timeslots = list(TimeSlot.objects.all())
        board_rows = []
        weekly_schedule_map = {day: [] for day, _ in TimeSlot.DAY_CHOICES}
        can_manage_timetable = self.request.user.role in {User.ROLE_ADMIN, User.ROLE_FACULTY}

        if term:
            entries = TimetableEntry.objects.filter(offering__term=term).select_related(
                "offering__course",
                "offering__faculty",
                "classroom",
                "timeslot",
            )
            focus_entries = entries
            if self.request.user.role == User.ROLE_FACULTY:
                focus_entries = focus_entries.filter(offering__faculty=self.request.user)
            elif self.request.user.role == User.ROLE_STUDENT:
                focus_entries = focus_entries.filter(offering__enrollments__student=self.request.user).distinct()

            for entry in entries:
                if entry.classroom_id:
                    cell_entries[f"{entry.timeslot_id}:{entry.classroom_id}"] = entry
            for entry in focus_entries.order_by(
                "timeslot__day_of_week",
                "timeslot__start_time",
                "offering__course__code",
            ):
                weekly_schedule_map[entry.timeslot.day_of_week].append(entry)

        for timeslot in timeslots:
            board_rows.append(
                {
                    "timeslot": timeslot,
                    "cells": [
                        {
                            "classroom": classroom,
                            "entry": cell_entries.get(f"{timeslot.id}:{classroom.id}"),
                        }
                        for classroom in classrooms
                    ],
                }
            )

        weekly_schedule = [
            {
                "label": label,
                "entries": weekly_schedule_map[day],
            }
            for day, label in TimeSlot.DAY_CHOICES
            if weekly_schedule_map[day]
        ]

        context.update(
            {
                "term": term,
                "entries": entries,
                "focus_entries": focus_entries,
                "cell_entries": cell_entries,
                "timeslots": timeslots,
                "days": TimeSlot.DAY_CHOICES,
                "conflicts": detect_timetable_conflicts(term) if term else [],
                "classrooms": classrooms,
                "board_rows": board_rows,
                "weekly_schedule": weekly_schedule,
                "can_manage_timetable": can_manage_timetable,
            }
        )
        return context


class GenerateTimetableView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = (User.ROLE_ADMIN, User.ROLE_FACULTY)

    def post(self, request):
        try:
            result = generate_timetable()
            messages.success(request, f"{result['created_count']} timetable slots were generated.")
            if result["unallocated"]:
                messages.warning(request, f"{len(result['unallocated'])} sessions still need manual review.")
        except ValidationError as exc:
            messages.error(request, exc.message)
        return redirect("academics:timetable_board")
