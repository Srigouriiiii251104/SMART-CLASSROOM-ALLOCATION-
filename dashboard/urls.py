from django.urls import path

from .views import DashboardAnalyticsAPIView, DashboardHomeView


app_name = "dashboard"

urlpatterns = [
    path("", DashboardHomeView.as_view(), name="home"),
    path("analytics/", DashboardAnalyticsAPIView.as_view(), name="analytics"),
]
