from unittest.mock import MagicMock, patch

from core.factories import UserFactory
from core.models import User
from core.services import AuthService
from django.test import TestCase


class AuthServiceTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory(is_verified=False)

    @patch("core.services.auth_service.get_language")
    @patch("core.services.auth_service.User.objects.create_user")
    @patch("core.services.auth_service.AuthService.trigger_verification_email")
    def test_register_user_success(self, mock_trigger, mock_create, mock_lang):
        mock_lang.return_value = "fr"
        mock_user = MagicMock(spec=User)
        mock_create.return_value = mock_user

        data = {
            "email": "new@test.com",
            "password": "pass",
            "first_name": "Jean",
            "username": "jean_user",
        }

        result = AuthService.register_user(data)

        self.assertEqual(result, mock_user)
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        self.assertEqual(call_kwargs["preferred_language"], "fr")
        mock_trigger.assert_called_once_with(mock_user)

    @patch("core.services.auth_service.get_language")
    @patch("core.services.auth_service.User.objects.create_user")
    @patch("core.services.auth_service.AuthService.trigger_verification_email")
    def test_register_user_no_language_fallback(
        self, mock_trigger, mock_create, mock_lang
    ):
        mock_lang.return_value = None
        mock_user = MagicMock(spec=User)
        mock_create.return_value = mock_user

        data = {
            "email": "nolang@test.com",
            "password": "pass",
        }

        AuthService.register_user(data)

        call_kwargs = mock_create.call_args[1]
        self.assertNotIn("preferred_language", call_kwargs)

    @patch("core.tasks.send_email_notification.delay")
    def test_trigger_email_verification_execution(self, mock_send):
        user = UserFactory(is_verified=False, preferred_language="en")

        AuthService.trigger_verification_email(user, language="es")

        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        self.assertEqual(kwargs["to_email"], user.email)
        self.assertEqual(kwargs["language"], "es")
        self.assertEqual(
            kwargs["context"]["verification_token"], user.verification_uuid.hex
        )

    @patch("core.services.auth_service.logger")
    @patch("core.tasks.send_email_notification.delay")
    def test_trigger_email_verification_already_verified(self, mock_send, mock_logger):
        verified_user = UserFactory(is_verified=True)

        AuthService.trigger_verification_email(verified_user)

        mock_send.assert_not_called()
        mock_logger.warning.assert_called()
