from django.contrib import admin

from .models import Announcement, Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "recipient", "category", "channel", "is_read", "created_at")
    list_filter = ("category", "channel", "is_read")
    search_fields = ("title", "recipient__username")


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "audience", "created_by", "expires_at", "created_at")
    list_filter = ("audience",)
