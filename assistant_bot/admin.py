from django.contrib import admin

from .models import ChatbotInteraction


@admin.register(ChatbotInteraction)
class ChatbotInteractionAdmin(admin.ModelAdmin):
    list_display = ("user", "channel", "query", "created_at")
    search_fields = ("query", "response", "user__username")
