from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ChatRequestSerializer
from .services import respond_to_query


class AssistantPageView(LoginRequiredMixin, TemplateView):
    template_name = "assistant_bot/chatbot.html"


class ChatbotAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = respond_to_query(serializer.validated_data["query"], request.user)
        return Response({"response": response}, status=status.HTTP_200_OK)
