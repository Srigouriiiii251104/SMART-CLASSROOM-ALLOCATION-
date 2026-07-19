from rest_framework import serializers


class ChatRequestSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=500)
