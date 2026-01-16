from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .user_serializers import MeSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = MeSerializer(self.user).data
        return data


class GoogleLoginSerializer(serializers.Serializer):
    token = serializers.CharField()
