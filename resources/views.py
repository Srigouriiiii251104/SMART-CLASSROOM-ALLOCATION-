from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from accounts.mixins import RoleRequiredMixin
from .forms import ResourceBookingForm, ResourceForm
from .models import Resource, ResourceBooking


class ResourceCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    allowed_roles = ("admin", "faculty")
    model = Resource
    form_class = ResourceForm
    template_name = "shared/form.html"
    success_url = reverse_lazy("resources:resource_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add Resource"
        return context


class ResourceListView(LoginRequiredMixin, ListView):
    model = Resource
    template_name = "resources/resource_list.html"
    context_object_name = "resources"


class ResourceBookingListView(LoginRequiredMixin, ListView):
    model = ResourceBooking
    template_name = "resources/booking_list.html"
    context_object_name = "bookings"

    def get_queryset(self):
        queryset = ResourceBooking.objects.select_related("resource", "requested_by", "classroom")
        if self.request.user.role == "student":
            queryset = queryset.filter(requested_by=self.request.user)
        return queryset


class ResourceBookingCreateView(LoginRequiredMixin, CreateView):
    model = ResourceBooking
    form_class = ResourceBookingForm
    template_name = "shared/form.html"
    success_url = reverse_lazy("resources:booking_list")

    def form_valid(self, form):
        form.instance.requested_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Book Resource"
        return context
