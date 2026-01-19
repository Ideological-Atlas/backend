import django.contrib.auth.password_validation as validators
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.serializers import ErrorDetail
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .user_serializers import MeSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = MeSerializer(self.user).data
        return data


class GoogleLoginSerializer(serializers.Serializer):
    token = serializers.CharField()


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    def validate_new_password(self, value):
        user = self.context.get("user")
        try:
            validators.validate_password(password=value, user=user)
        except DjangoValidationError as exception:
            raise serializers.ValidationError(
                [ErrorDetail(e.message, code=e.code) for e in exception.error_list]
            )
        return value
