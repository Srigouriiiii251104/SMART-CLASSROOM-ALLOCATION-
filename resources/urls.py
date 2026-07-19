from django.urls import path

from .api import ResourceAvailabilityAPIView, ResourceBookingAPIView
from .views import (
    ResourceBookingCreateView,
    ResourceBookingListView,
    ResourceCreateView,
    ResourceListView,
)


app_name = "resources"

urlpatterns = [
    path("", ResourceListView.as_view(), name="resource_list"),
    path("add/", ResourceCreateView.as_view(), name="resource_add"),
    path("bookings/", ResourceBookingListView.as_view(), name="booking_list"),
    path("bookings/add/", ResourceBookingCreateView.as_view(), name="booking_add"),
    path("api/availability/", ResourceAvailabilityAPIView.as_view(), name="api_availability"),
    path("api/bookings/", ResourceBookingAPIView.as_view(), name="api_bookings"),
]
