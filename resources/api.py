from datetime import datetime

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ResourceBooking
from .serializers import ResourceBookingSerializer, ResourceSerializer
from .services import find_available_resources


class ResourceAvailabilityAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        booking_date = request.query_params.get("date")
        start_time = request.query_params.get("start_time")
        end_time = request.query_params.get("end_time")
        if not booking_date or not start_time or not end_time:
            return Response(
                {"detail": "date, start_time, and end_time are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        resources = find_available_resources(
            booking_date=datetime.strptime(booking_date, "%Y-%m-%d").date(),
            start_time=datetime.strptime(start_time, "%H:%M").time(),
            end_time=datetime.strptime(end_time, "%H:%M").time(),
            category_id=request.query_params.get("category_id"),
        )
        return Response(ResourceSerializer(resources, many=True).data)


class ResourceBookingAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        bookings = ResourceBooking.objects.select_related("resource", "requested_by", "classroom")
        return Response(ResourceBookingSerializer(bookings, many=True).data)

    def post(self, request):
        serializer = ResourceBookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = ResourceBooking(requested_by=request.user, **serializer.validated_data)
        booking.full_clean()
        booking.save()
        return Response(ResourceBookingSerializer(booking).data, status=status.HTTP_201_CREATED)
