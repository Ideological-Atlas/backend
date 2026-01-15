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

        self.assertEqual(call_kwargs["username"], "jean_user")
        self.assertEqual(call_kwargs["email"], "new@test.com")
        self.assertEqual(call_kwargs["password"], "pass")
        self.assertEqual(call_kwargs["preferred_language"], "fr")
        self.assertEqual(call_kwargs["auth_provider"], User.AuthProvider.INTERNAL)

        self.assertEqual(call_kwargs["first_name"], "Jean")

        mock_trigger.assert_called_once_with(mock_user)

    @patch("core.tasks.send_email_notification.delay")
    def test_trigger_email_verification_success(self, mock_send):
        AuthService.trigger_verification_email(self.user, language="en")

        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        self.assertEqual(kwargs["to_email"], self.user.email)
        self.assertEqual(kwargs["language"], "en")

    @patch("core.services.auth_service.logger")
    @patch("core.tasks.send_email_notification.delay")
    def test_trigger_email_verification_already_verified(self, mock_send, mock_logger):
        self.user.is_verified = True
        self.user.save()

        AuthService.trigger_verification_email(self.user)

        mock_send.assert_not_called()
        mock_logger.warning.assert_called()
