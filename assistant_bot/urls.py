from django.urls import path

from .views import AssistantPageView, ChatbotAPIView


app_name = "assistant_bot"

urlpatterns = [
    path("", AssistantPageView.as_view(), name="chat"),
    path("api/query/", ChatbotAPIView.as_view(), name="api_query"),
]
