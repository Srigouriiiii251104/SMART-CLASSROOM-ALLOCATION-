from django.contrib import admin

from .models import MaintenanceRecord, Resource, ResourceBooking, ResourceCategory


@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "category", "classroom", "quantity", "available_quantity", "status")
    list_filter = ("category", "status", "is_portable")
    search_fields = ("name", "code")


@admin.register(ResourceBooking)
class ResourceBookingAdmin(admin.ModelAdmin):
    list_display = ("resource", "requested_by", "booking_date", "start_time", "end_time", "status")
    list_filter = ("status", "booking_date")
    search_fields = ("resource__name", "requested_by__username", "purpose")


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ("resource", "issue", "priority", "status", "scheduled_date")
    list_filter = ("priority", "status")
