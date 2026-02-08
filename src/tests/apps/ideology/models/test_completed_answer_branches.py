import uuid

from django.test import TestCase
from ideology.factories import (
    CompletedAnswerFactory,
    IdeologyAxisFactory,
    IdeologyConditionerFactory,
)


class CompletedAnswerBranchCoverageTestCase(TestCase):
    def test_map_axes_branches(self):
        axis = IdeologyAxisFactory()
        orphaned_uuid = uuid.uuid4().hex

        completed_answer = CompletedAnswerFactory(
            answers={
                "axis": [
                    {"uuid": "invalid-garbage", "value": 10},
                    {"uuid": orphaned_uuid, "value": 20},
                    {"uuid": axis.uuid.hex, "value": 30},
                ]
            }
        )

        mapped = completed_answer.get_mapped_for_calculation()

        self.assertNotIn("invalid-garbage", mapped)
        self.assertNotIn(orphaned_uuid, mapped)

        self.assertIn(axis.uuid.hex, mapped)
        self.assertEqual(mapped[axis.uuid.hex].value, 30)

    def test_map_conditioners_branches(self):
        cond = IdeologyConditionerFactory()

        completed_answer = CompletedAnswerFactory(
            answers={
                "conditioners": [
                    {"uuid": "bad-uuid", "value": "A"},
                    {"uuid": cond.uuid.hex, "value": "B"},
                ]
            }
        )

        mapped = completed_answer.get_mapped_for_calculation()

        self.assertNotIn("bad-uuid", mapped)
        self.assertIn(cond.uuid.hex, mapped)
        self.assertEqual(mapped[cond.uuid.hex].value, "B")
