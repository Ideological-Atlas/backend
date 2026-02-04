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

    def test_get_mapped_filters_malformed_and_orphaned_uuids(self):
        axis = IdeologyAxisFactory()
        orphaned_uuid = "00000000000000000000000000000000"

        completed_answer = CompletedAnswerFactory(
            answers={
                "axis": [
                    {"uuid": axis.uuid.hex, "value": 50},
                    {"uuid": "not-a-valid-uuid", "value": 10},
                    {"uuid": orphaned_uuid, "value": 20},
                ]
            }
        )

        mapped = completed_answer.get_mapped_for_calculation()

        self.assertIn(axis.uuid.hex, mapped)
        self.assertNotIn("not-a-valid-uuid", mapped)
        self.assertNotIn(orphaned_uuid, mapped)

        self.assertEqual(len(mapped), 1)

    def test_get_mapped_with_invalid_types_inside_dict(self):
        completed_answer = CompletedAnswerFactory(
            answers={
                "axis": [
                    {"uuid": 12345, "value": 10},
                    {"uuid": None, "value": 20},
                    {"uuid": [], "value": 30},
                ]
            }
        )
        mapped = completed_answer.get_mapped_for_calculation()
        self.assertEqual(mapped, {})

    def test_get_mapped_returns_empty_if_no_axis_data(self):
        completed_answer = CompletedAnswerFactory(answers={})
        mapped = completed_answer.get_mapped_for_calculation()
        self.assertEqual(mapped, {})

        completed_answer_empty_list = CompletedAnswerFactory(answers={"axis": []})
        mapped_empty = completed_answer_empty_list.get_mapped_for_calculation()
        self.assertEqual(mapped_empty, {})

    def test_get_mapped_handles_non_dict_items_in_list(self):
        # This triggers AttributeError on item.get("uuid") covering the last missing lines
        completed_answer = CompletedAnswerFactory(
            answers={"axis": [123, "string_item", None, ["list_item"]]}
        )
        mapped = completed_answer.get_mapped_for_calculation()
        self.assertEqual(mapped, {})
