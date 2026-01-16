from core.factories import UserFactory
from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from ideology.admin import UserAxisAnswerAdmin, UserConditionerAnswerAdmin
from ideology.factories import UserAxisAnswerFactory, UserConditionerAnswerFactory
from ideology.models import UserAxisAnswer, UserConditionerAnswer


class UserAxisAnswerAdminTestCase(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = UserAxisAnswerAdmin(UserAxisAnswer, self.site)

    def test_rendering(self):
        user = UserFactory(username="testuser")
        answer = UserAxisAnswerFactory(user=user)
        self.assertIn("testuser", str(answer))


class UserConditionerAnswerAdminTestCase(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = UserConditionerAnswerAdmin(UserConditionerAnswer, self.site)

    def test_rendering(self):
        user = UserFactory(username="testuser")
        answer = UserConditionerAnswerFactory(user=user)
        self.assertIn("testuser", str(answer))
