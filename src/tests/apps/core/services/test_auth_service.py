from unittest.mock import patch

from core.factories import UserFactory
from core.services import AuthService
from django.test import TestCase


class AuthServiceTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory(is_verified=False)

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
