from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import TemplateView

from .services import build_dashboard_context, build_dashboard_metrics


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(build_dashboard_context(self.request.user))
        return context


class DashboardAnalyticsAPIView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        return JsonResponse(build_dashboard_metrics(request.user))
