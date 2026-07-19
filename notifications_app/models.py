from django.conf import settings
from django.db import models


class Notification(models.Model):
    CHANNEL_APP = "app"
    CHANNEL_EMAIL = "email"
    CHANNEL_SMS = "sms"
    CHANNEL_TELEGRAM = "telegram"

    CHANNEL_CHOICES = [
        (CHANNEL_APP, "In App"),
        (CHANNEL_EMAIL, "Email"),
        (CHANNEL_SMS, "SMS"),
        (CHANNEL_TELEGRAM, "Telegram"),
    ]

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=150)
    message = models.TextField()
    category = models.CharField(max_length=50, default="general")
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default=CHANNEL_APP)
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} -> {self.recipient.display_name}"


class Announcement(models.Model):
    AUDIENCE_ALL = "all"
    AUDIENCE_FACULTY = "faculty"
    AUDIENCE_STUDENTS = "students"

    AUDIENCE_CHOICES = [
        (AUDIENCE_ALL, "All"),
        (AUDIENCE_FACULTY, "Faculty"),
        (AUDIENCE_STUDENTS, "Students"),
    ]

    title = models.CharField(max_length=150)
    message = models.TextField()
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default=AUDIENCE_ALL)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_announcements",
    )
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title
