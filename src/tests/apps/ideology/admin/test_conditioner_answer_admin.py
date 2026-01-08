from core.factories import UserFactory
from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from ideology.admin import ConditionerAnswerAdmin
from ideology.factories import ConditionerAnswerFactory, IdeologyFactory
from ideology.models import ConditionerAnswer


class ConditionerAnswerAdminTestCase(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = ConditionerAnswerAdmin(ConditionerAnswer, self.site)

    def test_get_subject(self):
        user = UserFactory.build(username="testuser")
        ideo = IdeologyFactory.build(name="TestIdeology")

        cases = [
            (
                ConditionerAnswerFactory.build(user=user, ideology=None),
                "User: testuser",
            ),
            (
                ConditionerAnswerFactory.build(trait_ideology=True, ideology=ideo),
                "Ideology: TestIdeology",
            ),
            (ConditionerAnswerFactory.build(user=None, ideology=None), "-"),
        ]

        for instance, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(self.admin.get_subject(instance), expected)
