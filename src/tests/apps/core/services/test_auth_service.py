import uuid
from unittest.mock import patch

from core.factories import UserFactory, VerifiedUserFactory
from core.services import AuthService
from django.test import TestCase


class AuthServiceTestCase(TestCase):
    @patch("core.services.auth_service.get_language")
    @patch("core.services.auth_service.User.objects.create_user")
    @patch("core.services.auth_service.send_email_notification.delay")
    def test_register_user_execution_flow(self, mock_send, mock_create, mock_lang):
        mock_lang.return_value = "fr"
        user_instance = UserFactory.build(
            is_verified=False,
            preferred_language="fr",
            email="new@test.com",
            verification_uuid=uuid.uuid4(),
        )
        mock_create.return_value = user_instance
        data = {"email": "new@test.com", "password": "pass", "username": "testuser"}
        result = AuthService.register_user(data)
        self.assertEqual(result, user_instance)
        self.assertTrue(mock_create.called)
        self.assertEqual(mock_create.call_args[1]["preferred_language"], "fr")
        mock_send.assert_called_once()
        self.assertEqual(mock_send.call_args[1]["language"], "fr")
        self.assertEqual(mock_send.call_args[1]["to_email"], "new@test.com")

    @patch("core.services.auth_service.logger")
    @patch("core.services.auth_service.send_email_notification.delay")
    def test_trigger_verification_already_verified(self, mock_send, mock_logger):
        user = VerifiedUserFactory.build()
        AuthService.trigger_verification_email(user)
        mock_logger.warning.assert_called_once()
        mock_send.assert_not_called()

    @patch("core.services.auth_service.send_email_notification.delay")
    def test_trigger_verification_not_verified_explicit_language(self, mock_send):
        user = UserFactory.build(is_verified=False, preferred_language="es")
        AuthService.trigger_verification_email(user, language="en")
        mock_send.assert_called_once()
        self.assertEqual(mock_send.call_args[1]["language"], "en")

    @patch("core.services.auth_service.send_email_notification.delay")
    def test_trigger_verification_not_verified_user_language(self, mock_send):
        user = UserFactory.build(is_verified=False, preferred_language="it")
        AuthService.trigger_verification_email(user)
        mock_send.assert_called_once()
        self.assertEqual(mock_send.call_args[1]["language"], "it")
