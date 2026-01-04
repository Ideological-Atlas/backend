from datetime import timedelta
from unittest.mock import patch

from core.factories import UserFactory
from core.models import User
from core.tasks.maintenance import delete_unverified_users
from django.test import TestCase
from django.utils import timezone


class MaintenanceTasksTestCase(TestCase):
    @patch("core.tasks.maintenance.send_email_notification.delay")
    def test_delete_unverified_users_logic(self, mock_send):
        now = timezone.now()

        user_to_delete = UserFactory(is_verified=False, email="del@test.com")
        User.objects.filter(pk=user_to_delete.pk).update(
            created=now - timedelta(days=32)
        )

        user_safe_verified = UserFactory(is_verified=True, email="safe1@test.com")
        User.objects.filter(pk=user_safe_verified.pk).update(
            created=now - timedelta(days=40)
        )

        user_safe_recent = UserFactory(is_verified=False, email="safe2@test.com")
        User.objects.filter(pk=user_safe_recent.pk).update(
            created=now - timedelta(days=30)
        )

        delete_unverified_users()

        mock_send.assert_called_once()
        self.assertEqual(mock_send.call_args.kwargs["to_email"], "del@test.com")
        self.assertEqual(
            mock_send.call_args.kwargs["template_name"],
            "user_deleted_due_no_verification",
        )

        self.assertFalse(User.objects.filter(pk=user_to_delete.pk).exists())
        self.assertTrue(User.objects.filter(pk=user_safe_verified.pk).exists())
        self.assertTrue(User.objects.filter(pk=user_safe_recent.pk).exists())
