from unittest.mock import patch

from core.exceptions.user_exceptions import UserAlreadyVerifiedException
from core.factories import UserFactory, VerifiedUserFactory
from core.models import User
from django.test import TestCase


class UserModelTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_verify_user_flow(self):
        self.assertFalse(self.user.is_verified)
        self.user.verify()
        self.assertTrue(self.user.is_verified)
        with self.assertRaises(UserAlreadyVerifiedException):
            self.user.verify()

    def test_str_representation(self):
        self.assertEqual(str(self.user), self.user.username)

    def test_default_values(self):
        self.assertEqual(self.user.appearance, User.Appearance.AUTO)
        self.assertFalse(self.user.is_public)

    @patch("core.models.user.logger")
    @patch("core.models.user.transaction.on_commit")
    def test_trigger_verification_already_verified(self, mock_on_commit, mock_logger):
        verified_user = VerifiedUserFactory.build()
        verified_user.send_verification_email()
        mock_logger.warning.assert_called_once()
        mock_on_commit.assert_not_called()

    @patch("core.models.user.transaction.on_commit")
    def test_trigger_verification_not_verified_explicit_language(self, mock_on_commit):
        user = UserFactory.build(is_verified=False, preferred_language="es")
        user.send_verification_email(language="en")
        mock_on_commit.assert_called_once()

    @patch("core.models.user.transaction.on_commit")
    def test_trigger_verification_not_verified_user_language(self, mock_on_commit):
        user = UserFactory.build(is_verified=False, preferred_language="it")
        user.send_verification_email()
        mock_on_commit.assert_called_once()

    @patch("core.tasks.security.clear_reset_password_token.apply_async")
    @patch("core.tasks.notifications.send_email_notification.delay")
    def test_initiate_password_reset_with_email(self, mock_email, mock_celery):
        with self.captureOnCommitCallbacks(execute=True):
            self.user.initiate_password_reset(send_notification=True)

        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.reset_password_uuid)

        mock_email.assert_called_once()
        self.assertEqual(mock_email.call_args.kwargs["template_name"], "reset_password")
        self.assertEqual(
            mock_email.call_args.kwargs["context"]["reset_token"],
            self.user.reset_password_uuid.hex,
        )

        mock_celery.assert_called_once()
        self.assertEqual(mock_celery.call_args.kwargs["countdown"], 1800)

    @patch("core.tasks.security.clear_reset_password_token.apply_async")
    @patch("core.tasks.notifications.send_email_notification.delay")
    def test_initiate_password_reset_silent(self, mock_email, mock_celery):
        with self.captureOnCommitCallbacks(execute=True):
            self.user.initiate_password_reset(send_notification=False)

        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.reset_password_uuid)

        mock_email.assert_not_called()

        mock_celery.assert_called_once()
