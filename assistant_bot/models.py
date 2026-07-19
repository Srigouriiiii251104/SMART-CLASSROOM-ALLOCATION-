from django.conf import settings
from django.db import models


class ChatbotInteraction(models.Model):
    CHANNEL_WEB = "web"
    CHANNEL_VOICE = "voice"

    CHANNEL_CHOICES = [
        (CHANNEL_WEB, "Web"),
        (CHANNEL_VOICE, "Voice"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chatbot_interactions",
    )
    query = models.TextField()
    response = models.TextField()
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default=CHANNEL_WEB)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.query[:60]
