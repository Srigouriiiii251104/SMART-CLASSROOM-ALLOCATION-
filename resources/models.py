from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class ResourceCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Resource(models.Model):
    STATUS_AVAILABLE = "available"
    STATUS_RESERVED = "reserved"
    STATUS_MAINTENANCE = "maintenance"
    STATUS_RETIRED = "retired"

    STATUS_CHOICES = [
        (STATUS_AVAILABLE, "Available"),
        (STATUS_RESERVED, "Reserved"),
        (STATUS_MAINTENANCE, "Maintenance"),
        (STATUS_RETIRED, "Retired"),
    ]

    category = models.ForeignKey(ResourceCategory, on_delete=models.CASCADE, related_name="resources")
    classroom = models.ForeignKey(
        "academics.Classroom",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resources",
    )
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=40, unique=True)
    quantity = models.PositiveIntegerField(default=1)
    available_quantity = models.PositiveIntegerField(default=1)
    is_portable = models.BooleanField(default=True)
    maintenance_cycle_days = models.PositiveIntegerField(default=90)
    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["category__name", "name"]

    def clean(self):
        if self.available_quantity > self.quantity:
            raise ValidationError("Available quantity cannot exceed total quantity.")

    def save(self, *args, **kwargs):
        if not self.available_quantity:
            self.available_quantity = self.quantity
        if self.last_maintenance_date and not self.next_maintenance_date:
            self.next_maintenance_date = self.last_maintenance_date + timedelta(days=self.maintenance_cycle_days)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class ResourceBooking(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="bookings")
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resource_bookings")
    classroom = models.ForeignKey(
        "academics.Classroom",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resource_bookings",
    )
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    quantity = models.PositiveIntegerField(default=1)
    purpose = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-booking_date", "start_time"]

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be later than start time.")
        if self.quantity > self.resource.quantity:
            raise ValidationError("Requested quantity exceeds inventory.")

        overlapping = ResourceBooking.objects.filter(
            resource=self.resource,
            booking_date=self.booking_date,
            status__in=[self.STATUS_PENDING, self.STATUS_APPROVED, self.STATUS_COMPLETED],
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exclude(pk=self.pk)
        reserved_quantity = sum(overlapping.values_list("quantity", flat=True))
        if reserved_quantity + self.quantity > self.resource.quantity:
            raise ValidationError("Resource quantity is not available for the selected time range.")

        # Check for schedule clashes with academic classes in the same room
        target_room = self.classroom or self.resource.classroom
        if target_room and self.booking_date and self.start_time and self.end_time:
            from academics.models import TimetableEntry
            day_of_week = self.booking_date.weekday()
            clashing_classes = TimetableEntry.objects.filter(
                classroom=target_room,
                timeslot__day_of_week=day_of_week,
                timeslot__start_time__lt=self.end_time,
                timeslot__end_time__gt=self.start_time,
            )
            if clashing_classes.exists():
                clashing_class = clashing_classes.first()
                raise ValidationError(
                    f"Classroom {target_room.name} has a scheduled class ({clashing_class.offering.course.code}) during this time slot."
                )

    def __str__(self) -> str:
        return f"{self.resource.name} on {self.booking_date}"


class MaintenanceRecord(models.Model):
    STATUS_OPEN = "open"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_RESOLVED = "resolved"

    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_RESOLVED, "Resolved"),
    ]

    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Low"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_HIGH, "High"),
    ]

    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="maintenance_records")
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reported_maintenance_issues",
    )
    issue = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    scheduled_date = models.DateField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["status", "priority"]

    def __str__(self) -> str:
        return f"{self.resource.name} - {self.issue}"
