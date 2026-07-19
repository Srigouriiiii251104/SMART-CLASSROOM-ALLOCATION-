from datetime import date, timedelta

from .models import MaintenanceRecord, Resource, ResourceBooking


def find_available_resources(booking_date, start_time, end_time, category_id=None):
    resources = Resource.objects.filter(status=Resource.STATUS_AVAILABLE)
    if category_id:
        resources = resources.filter(category_id=category_id)

    available_ids = []
    for resource in resources:
        overlapping = ResourceBooking.objects.filter(
            resource=resource,
            booking_date=booking_date,
            status__in=[
                ResourceBooking.STATUS_PENDING,
                ResourceBooking.STATUS_APPROVED,
                ResourceBooking.STATUS_COMPLETED,
            ],
            start_time__lt=end_time,
            end_time__gt=start_time,
        )
        booked_quantity = sum(overlapping.values_list("quantity", flat=True))
        if booked_quantity < resource.quantity:
            available_ids.append(resource.id)
    return Resource.objects.filter(id__in=available_ids).select_related("category", "classroom")


def due_maintenance_resources(window_days: int = 7):
    today = date.today()
    return Resource.objects.filter(
        next_maintenance_date__isnull=False,
        next_maintenance_date__lte=today + timedelta(days=window_days),
    )


def open_maintenance_alerts():
    return MaintenanceRecord.objects.exclude(status=MaintenanceRecord.STATUS_RESOLVED)
