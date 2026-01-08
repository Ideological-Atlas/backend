from core.factories import UserFactory
from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from ideology.admin import AxisAnswerAdmin
from ideology.factories import AxisAnswerFactory, IdeologyFactory
from ideology.models import AxisAnswer


class AxisAnswerAdminTestCase(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = AxisAnswerAdmin(AxisAnswer, self.site)

    def test_get_subject(self):
        user = UserFactory.build(username="testuser")
        ideo = IdeologyFactory.build(name="TestIdeology")

        cases = [
            (AxisAnswerFactory.build(user=user, ideology=None), "User: testuser"),
            (
                AxisAnswerFactory.build(trait_ideology=True, ideology=ideo),
                "Ideology: TestIdeology",
            ),
            (AxisAnswerFactory.build(user=None, ideology=None), "-"),
        ]

        for instance, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(self.admin.get_subject(instance), expected)
