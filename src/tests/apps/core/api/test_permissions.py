from unittest.mock import Mock

from core.api.permissions import IsVerified
from core.factories import UserFactory
from django.test import TestCase


class IsVerifiedPermissionTestCase(TestCase):
    def setUp(self):
        self.permission = IsVerified()
        self.view = Mock()
        self.request = Mock()

    def test_has_permission_true(self):
        self.request.user = UserFactory(is_verified=True)
        self.assertTrue(self.permission.has_permission(self.request, self.view))

    def test_has_permission_false(self):
        self.request.user = UserFactory(is_verified=False)
        self.assertFalse(self.permission.has_permission(self.request, self.view))
