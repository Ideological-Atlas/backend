import logging

import django.contrib.auth.password_validation as validators
from core.exceptions import api_exceptions
from core.exceptions.user_exceptions import UserAlreadyVerifiedException
from core.helpers import UUIDModelSerializerMixin
from core.models import User
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.serializers import ErrorDetail

logger = logging.getLogger(__name__)


class SimpleUserSerializer(UUIDModelSerializerMixin):
    class Meta:
        model = User
        fields = ["uuid", "username", "preferred_language"]


class UserVerificationSerializer(SimpleUserSerializer):
    class Meta(SimpleUserSerializer.Meta):
        fields = SimpleUserSerializer.Meta.fields + ["is_verified"]

    def update(self, instance, validated_data):
        try:
            instance.verify()
            return instance
        except UserAlreadyVerifiedException as exception:
            logger.error(exception)
            raise api_exceptions.ForbiddenException(exception)


class MeSerializer(SimpleUserSerializer):
    class Meta:
        model = User
        fields = [
            "uuid",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_verified",
            "preferred_language",
            "auth_provider",
        ]
        read_only_fields = ["is_verified", "email", "auth_provider"]


class RegisterSerializer(UUIDModelSerializerMixin):
    password = serializers.CharField(
        write_only=True, help_text=_("Password of the user")
    )
    username = serializers.CharField(required=False, help_text=_("Username"))

    class Meta:
        model = User
        fields = ["uuid", "email", "password", "username"]

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get("password")
        errors = {}

        try:
            validators.validate_password(password=password, user=user)
        except DjangoValidationError as exception:
            errors["password"] = [
                ErrorDetail(e.message, code=e.code) for e in exception.error_list
            ]

        if errors:
            raise serializers.ValidationError(errors)

        return super().validate(attrs)

    def create(self, validated_data):  # pylint: disable=E1134, W0221
        username = validated_data.pop("username", None)

        current_language = get_language()
        if current_language:
            validated_data["preferred_language"] = current_language

        user = User.objects.create_user(
            username=username,
            auth_provider=User.AuthProvider.INTERNAL,
            **validated_data
        )  # pylint: disable=W0221
        user.trigger_email_verification()
        return user


class GoogleLoginSerializer(serializers.Serializer):
    token = serializers.CharField(
        help_text=_("Google ID Token provided by the frontend.")
    )


class UserSetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True)

    @staticmethod
    def validate_new_password(value):
        validators.validate_password(value)
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance
