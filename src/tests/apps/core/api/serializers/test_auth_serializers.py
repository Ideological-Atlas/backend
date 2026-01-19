from unittest.mock import patch

from core.api.api_test_helpers import SerializerTestBase
from core.api.serializers import PasswordResetConfirmSerializer
from django.core.exceptions import ValidationError as DjangoValidationError


class AuthSerializersTestCase(SerializerTestBase):

    @patch("django.contrib.auth.password_validation.validate_password")
    def test_password_reset_confirm_serializer_validates_password(self, mock_validate):
        data = {"new_password": "StrongPassword123!"}
        serializer = PasswordResetConfirmSerializer(
            data=data, context={"user": self.user}
        )
        self.assertTrue(serializer.is_valid())
        mock_validate.assert_called_once_with(
            password="StrongPassword123!", user=self.user
        )

    @patch("django.contrib.auth.password_validation.validate_password")
    def test_password_reset_confirm_serializer_handles_django_validation_error(
        self, mock_validate
    ):
        mock_validate.side_effect = DjangoValidationError(
            "Password is too common", code="password_too_common"
        )

        data = {"new_password": "123"}
        serializer = PasswordResetConfirmSerializer(
            data=data, context={"user": self.user}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("new_password", serializer.errors)
        self.assertEqual(
            serializer.errors["new_password"][0].code, "password_too_common"
        )
