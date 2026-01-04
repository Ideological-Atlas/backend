from unittest.mock import patch

from core.api.api_test_helpers import SerializerTestBase
from core.api.serializers import (
    MeSerializer,
    RegisterSerializer,
    UserVerificationSerializer,
)
from core.exceptions import api_exceptions
from core.exceptions.user_exceptions import UserAlreadyVerifiedException
from core.factories import UserFactory
from django.utils import translation
from rest_framework.exceptions import ValidationError


class RegisterSerializerTestCase(SerializerTestBase):
    def setUp(self):
        super().setUp()
        self.data = {"email": "new@test.com", "password": "StrongPassword1!"}

    @patch("core.models.user.User.trigger_email_verification")
    def test_create_flow(self, mock_trigger):
        serializer = RegisterSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, self.data["email"])
        mock_trigger.assert_called_once()

    def test_create_sets_preferred_language(self):
        with translation.override("en"):
            serializer = RegisterSerializer(data=self.data)
            self.assertTrue(serializer.is_valid())
            user = serializer.save()
            self.assertEqual(user.preferred_language, "en")

    @patch("core.models.user.User.trigger_email_verification")
    @patch("core.api.serializers.user_serializers.get_language")
    def test_create_fallback_language(self, mock_get_language, mock_trigger):
        mock_get_language.return_value = None
        serializer = RegisterSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.preferred_language, "es")
        mock_trigger.assert_called_once()

    def test_validate_password_errors(self):
        self.data["password"] = "123"  # nosec
        serializer = RegisterSerializer(data=self.data)

        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)

        self.assertIn("password", cm.exception.detail)
        self.assertEqual(cm.exception.detail["password"][0].code, "password_too_short")

    def test_create_method_username_logic(self):
        data_auto = self.data.copy()
        data_auto["email"] = "auto@test.com"

        serializer = RegisterSerializer(data=data_auto)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertIsNotNone(user.username)

        data_custom = self.data.copy()
        data_custom["email"] = "custom@test.com"
        data_custom["username"] = "custom_user"

        serializer = RegisterSerializer(data=data_custom)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.username, "custom_user")


class VerificationSerializerTestCase(SerializerTestBase):
    def test_verification_logic(self):
        user = UserFactory(is_verified=False)
        serializer = UserVerificationSerializer(user, data={}, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        user.refresh_from_db()
        self.assertTrue(user.is_verified)

    def test_already_verified_raises_forbidden(self):
        user = UserFactory(is_verified=True)
        serializer = UserVerificationSerializer(user, data={}, partial=True)
        self.assertTrue(serializer.is_valid())

        with patch.object(
            user, "verify", side_effect=UserAlreadyVerifiedException(user)
        ):
            with self.assertRaises(api_exceptions.ForbiddenException):
                serializer.update(user, serializer.validated_data)


class MeSerializerTestCase(SerializerTestBase):
    def test_fields(self):
        serializer = MeSerializer(self.user)
        self.assertTrue(serializer.data["username"])
        self.assertIn("uuid", serializer.data)
        self.assertIn("preferred_language", serializer.data)

    def test_update_preferred_language(self):
        data = {"preferred_language": "fr"}
        serializer = MeSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.preferred_language, "fr")
