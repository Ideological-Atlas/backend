from unittest.mock import patch

from core.api.api_test_helpers import SerializerTestBase
from core.api.serializers import (
    MeSerializer,
    RegisterSerializer,
    UserSetPasswordSerializer,
    UserVerificationSerializer,
)
from core.exceptions import api_exceptions
from core.exceptions.user_exceptions import UserAlreadyVerifiedException
from core.factories import UserFactory
from core.models import User
from rest_framework.exceptions import ValidationError


class RegisterSerializerTestCase(SerializerTestBase):
    def setUp(self):
        super().setUp()
        self.data = {"email": "new@test.com", "password": "StrongPassword1!"}

    def test_create_flow_only_creates_user(self):
        serializer = RegisterSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()

        self.assertEqual(user.email, self.data["email"])
        self.assertEqual(user.auth_provider, "internal")

    def test_validate_password_errors(self):
        self.data["password"] = "123"
        serializer = RegisterSerializer(data=self.data)

        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)

        self.assertIn("password", cm.exception.detail)
        self.assertEqual(cm.exception.detail["password"][0].code, "password_too_short")


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
    def test_fields_structure(self):
        serializer = MeSerializer(self.user)
        data = serializer.data
        self.assertTrue(data["username"])
        self.assertIn("uuid", data)
        self.assertIn("preferred_language", data)
        self.assertIn("auth_provider", data)
        self.assertIn("appearance", data)
        self.assertIn("is_public", data)
        self.assertNotIn("has_password", data)

    def test_update_settings(self):
        data = {
            "preferred_language": "fr",
            "appearance": User.Appearance.DARK,
            "is_public": True,
        }
        serializer = MeSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.preferred_language, "fr")
        self.assertEqual(self.user.appearance, User.Appearance.DARK)
        self.assertTrue(self.user.is_public)


class UserSetPasswordSerializerTestCase(SerializerTestBase):
    def test_set_password_success(self):
        new_pass = "NewStrongPassword1!"
        data = {"new_password": new_pass}
        serializer = UserSetPasswordSerializer(self.user, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_pass))

    def test_set_password_weak_fails(self):
        data = {"new_password": "123"}
        serializer = UserSetPasswordSerializer(self.user, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("new_password", serializer.errors)
