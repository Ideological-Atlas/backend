from core.factories import UserFactory
from django.test import TestCase
from ideology.factories import (
    CompletedAnswerFactory,
    IdeologyAxisFactory,
)


class CompletedAnswerModelTestCase(TestCase):
    def test_str_authenticated_user(self):
        user = UserFactory(username="tester")
        completed_answer = CompletedAnswerFactory(completed_by=user)
        self.assertIn("tester", str(completed_answer))

    def test_str_anonymous_user(self):
        completed_answer = CompletedAnswerFactory(completed_by=None)
        self.assertIn("Anonymous", str(completed_answer))

    def test_get_mapped_filters_deleted_axes(self):
        axis = IdeologyAxisFactory()
        completed_answer = CompletedAnswerFactory(
            answers={"axis": [{"uuid": axis.uuid.hex, "value": 50}]}
        )

        initial_map = completed_answer.get_mapped_for_calculation()
        self.assertIn(axis.uuid.hex, initial_map)

        axis.delete()

        final_map = completed_answer.get_mapped_for_calculation()
        self.assertNotIn(axis.uuid.hex, final_map)
