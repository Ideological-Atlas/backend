from unittest.mock import Mock, patch

from core.admin.user_admin import CustomUserAdmin
from core.factories import UserFactory
from core.models import User
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase


class UserAdminTestCase(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = CustomUserAdmin(User, self.site)
        self.factory = RequestFactory()

    @patch("core.models.User.send_verification_email")
    def test_send_verification_email_action(self, mock_send_email):
        user1 = UserFactory()
        user2 = UserFactory()
        queryset = User.objects.filter(id__in=[user1.id, user2.id])
        request = self.factory.get("/")
        self.admin.message_user = Mock()
        self.admin.send_verification_email(request, queryset)
        self.assertEqual(mock_send_email.call_count, 2)
        self.admin.message_user.assert_called_once()
