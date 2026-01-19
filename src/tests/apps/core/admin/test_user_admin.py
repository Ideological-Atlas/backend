from unittest.mock import Mock, patch

from core.admin.user_admin import CustomUserAdmin
from core.factories import UserFactory
from core.models import User
from django.contrib import messages
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase
from django.utils import translation


class UserAdminTestCase(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = CustomUserAdmin(User, self.site)
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.admin.message_user = Mock()

    @patch("core.models.User.send_verification_email")
    def test_send_verification_email_action(self, mock_send_email):
        user1 = UserFactory()
        user2 = UserFactory()
        queryset = User.objects.filter(id__in=[user1.id, user2.id])

        with translation.override("en"):
            self.admin.send_verification_email(self.request, queryset)

            self.assertEqual(mock_send_email.call_count, 2)
            self.admin.message_user.assert_called_with(
                self.request,
                "Verification emails process started for selected users.",
                messages.SUCCESS,
            )

    @patch("core.models.User.initiate_password_reset")
    def test_trigger_password_reset_action(self, mock_initiate):
        user = UserFactory()
        queryset = User.objects.filter(id=user.id)

        with translation.override("en"):
            self.admin.trigger_password_reset(self.request, queryset)

            mock_initiate.assert_called_once_with(send_notification=True)
            self.admin.message_user.assert_called_with(
                self.request,
                "Password reset initiated with email for selected users.",
                messages.SUCCESS,
            )

    @patch("core.models.User.initiate_password_reset")
    def test_trigger_password_reset_silent_action(self, mock_initiate):
        user = UserFactory()
        queryset = User.objects.filter(id=user.id)

        with translation.override("en"):
            self.admin.trigger_password_reset_silent(self.request, queryset)

            mock_initiate.assert_called_once_with(send_notification=False)
            self.admin.message_user.assert_called_with(
                self.request,
                "Password reset token generated silently. No email sent.",
                messages.SUCCESS,
            )
