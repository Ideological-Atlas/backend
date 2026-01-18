from core.factories import UserFactory
from django.test import TestCase
from ideology.factories import CompletedAnswerFactory


class CompletedAnswerModelTestCase(TestCase):
    def test_str_authenticated_user(self):
        user = UserFactory(username="tester")
        completed_answer = CompletedAnswerFactory(completed_by=user)
        self.assertIn("tester", str(completed_answer))

    def test_str_anonymous_user(self):
        completed_answer = CompletedAnswerFactory(completed_by=None)
        self.assertIn("Anonymous", str(completed_answer))
