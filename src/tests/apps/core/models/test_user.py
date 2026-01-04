from unittest.mock import patch

from core.exceptions.user_exceptions import UserAlreadyVerifiedException
from core.factories import UserFactory
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

    # CORRECCIÓN: Parcheamos 'core.tasks.send_email_notification.delay'
    # porque el import ahora es local dentro de la función.
    @patch("core.tasks.send_email_notification.delay")
    def test_trigger_email_verification(self, mock_send):
        # Case 1: Success
        self.user.trigger_email_verification(language="en")
        mock_send.assert_called_once()

        # Case 2: Already verified (logs warning, early return)
        mock_send.reset_mock()
        self.user.is_verified = True
        self.user.trigger_email_verification()
        mock_send.assert_not_called()
