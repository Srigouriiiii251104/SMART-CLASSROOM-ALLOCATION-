from rest_framework import serializers

from .models import Resource, ResourceBooking


class ResourceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Resource
        fields = [
            "id",
            "name",
            "code",
            "category",
            "category_name",
            "classroom",
            "quantity",
            "available_quantity",
            "status",
            "is_portable",
            "next_maintenance_date",
        ]


class ResourceBookingSerializer(serializers.ModelSerializer):
    resource_name = serializers.CharField(source="resource.name", read_only=True)
    requested_by_name = serializers.CharField(source="requested_by.display_name", read_only=True)

    class Meta:
        model = ResourceBooking
        fields = [
            "id",
            "resource",
            "resource_name",
            "requested_by",
            "requested_by_name",
            "classroom",
            "booking_date",
            "start_time",
            "end_time",
            "quantity",
            "purpose",
            "status",
            "notes",
        ]
        read_only_fields = ["requested_by", "status"]
