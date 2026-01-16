from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from core.factories import UserFactory
from core.models import User
from core.tasks.reminders import send_verification_reminders
from django.test import TestCase


class VerificationRemindersTestCase(TestCase):
    @patch("core.tasks.reminders.send_email_notification.delay")
    @patch("django.utils.timezone.now")
    def test_send_verification_reminders_logic(self, mock_now, mock_send):
        fixed_now = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        mock_now.return_value = fixed_now

        def create_target_user(days_ago, is_verified=False, email_prefix="user"):
            user = UserFactory(
                is_verified=is_verified, email=f"{email_prefix}_{days_ago}@test.com"
            )
            past_date = fixed_now - timedelta(days=days_ago)
            User.objects.filter(pk=user.pk).update(created=past_date)
            return user

        u3 = create_target_user(3, email_prefix="target")
        u7 = create_target_user(7, email_prefix="target")
        u30 = create_target_user(30, email_prefix="target")
        create_target_user(2, email_prefix="noise")
        create_target_user(31, email_prefix="noise")
        create_target_user(3, is_verified=True, email_prefix="verified")
        send_verification_reminders()
        self.assertEqual(mock_send.call_count, 3)
        calls = mock_send.call_args_list
        sent_emails = [call.kwargs["to_email"] for call in calls]
        sent_templates = [call.kwargs["template_name"] for call in calls]
        self.assertIn(u3.email, sent_emails)
        self.assertIn(u7.email, sent_emails)
        self.assertIn(u30.email, sent_emails)
        self.assertIn("registration_reminder_3_days", sent_templates)
        self.assertIn("registration_reminder_7_days", sent_templates)
        self.assertIn("registration_reminder_30_days", sent_templates)
