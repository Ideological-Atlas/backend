import uuid

from core.factories import UserFactory
from django.test import TestCase
from ideology.factories import (
    IdeologyAxisFactory,
    IdeologyConditionerFactory,
    UserAxisAnswerFactory,
    UserConditionerAnswerFactory,
)
from ideology.models import CompletedAnswer


class CompletedAnswerManagerTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_given_authenticated_user_with_db_answers_when_generate_snapshot_then_creates_record_from_db_state(
        self,
    ):
        ideology_axis = IdeologyAxisFactory()
        ideology_conditioner = IdeologyConditionerFactory()

        UserAxisAnswerFactory(
            user=self.user,
            axis=ideology_axis,
            value=50,
            margin_left=5,
            margin_right=5,
        )
        UserConditionerAnswerFactory(
            user=self.user, conditioner=ideology_conditioner, answer="Yes"
        )

        completed_answer_snapshot = CompletedAnswer.objects.generate_snapshot(
            user=self.user
        )

        self.assertEqual(completed_answer_snapshot.completed_by, self.user)
        answers_data = completed_answer_snapshot.answers

        self.assertIn("axis", answers_data)
        self.assertIn("conditioners", answers_data)

        self.assertEqual(len(answers_data["axis"]), 1)
        self.assertEqual(answers_data["axis"][0]["uuid"], ideology_axis.uuid.hex)
        self.assertEqual(answers_data["axis"][0]["value"], 50)

        self.assertEqual(len(answers_data["conditioners"]), 1)
        self.assertEqual(
            answers_data["conditioners"][0]["uuid"], ideology_conditioner.uuid.hex
        )
        self.assertEqual(answers_data["conditioners"][0]["value"], "Yes")

    def test_given_authenticated_user_when_generate_snapshot_twice_then_returns_idempotent_result_unless_data_changes(
        self,
    ):
        ideology_axis = IdeologyAxisFactory()
        UserAxisAnswerFactory(user=self.user, axis=ideology_axis, value=50)

        first_snapshot = CompletedAnswer.objects.generate_snapshot(user=self.user)

        with self.subTest("Should return existing instance for identical data"):
            second_snapshot = CompletedAnswer.objects.generate_snapshot(user=self.user)

            self.assertEqual(first_snapshot.pk, second_snapshot.pk)
            self.assertEqual(first_snapshot.answer_hash, second_snapshot.answer_hash)
            self.assertEqual(CompletedAnswer.objects.count(), 1)

        with self.subTest("Should create new instance for modified data"):
            UserAxisAnswerFactory(user=self.user, axis=IdeologyAxisFactory(), value=10)

            third_snapshot = CompletedAnswer.objects.generate_snapshot(user=self.user)

            self.assertNotEqual(first_snapshot.pk, third_snapshot.pk)
            self.assertNotEqual(first_snapshot.answer_hash, third_snapshot.answer_hash)
            self.assertEqual(CompletedAnswer.objects.count(), 2)

    def test_given_anonymous_user_with_input_data_when_generate_snapshot_then_normalizes_and_saves_data(
        self,
    ):
        axis_uuid = uuid.UUID("11111111111111111111111111111111")
        conditioner_uuid = uuid.UUID("22222222222222222222222222222222")

        raw_input_data = {
            "axis": [
                {
                    "uuid": axis_uuid,
                    "value": 10,
                    "margin_left": 0,
                    "margin_right": 0,
                }
            ],
            "conditioners": [
                {
                    "uuid": conditioner_uuid,
                    "value": "Option_A",
                }
            ],
        }

        completed_answer_snapshot = CompletedAnswer.objects.generate_snapshot(
            user=None, input_data=raw_input_data
        )

        self.assertIsNone(completed_answer_snapshot.completed_by)
        self.assertEqual(
            completed_answer_snapshot.answers["axis"][0]["uuid"],
            axis_uuid.hex,
        )

    def test_given_anonymous_input_when_generate_snapshot_twice_then_returns_idempotent_result_unless_data_changes(
        self,
    ):
        raw_input_data = {
            "axis": [{"uuid": uuid.UUID("a" * 32), "value": 10}],
            "conditioners": [],
        }

        with self.subTest("Should return existing instance for identical data"):
            first_snapshot = CompletedAnswer.objects.generate_snapshot(
                user=None, input_data=raw_input_data
            )
            second_snapshot = CompletedAnswer.objects.generate_snapshot(
                user=None, input_data=raw_input_data
            )

            self.assertEqual(first_snapshot.pk, second_snapshot.pk)
            self.assertEqual(
                first_snapshot.answer_hash,
                second_snapshot.answer_hash,
            )
            self.assertEqual(CompletedAnswer.objects.count(), 1)

        with self.subTest("Should create new instance for modified data"):
            modified_input_data = {
                "axis": [{"uuid": uuid.UUID("b" * 32), "value": 20}],
                "conditioners": [],
            }
            third_snapshot = CompletedAnswer.objects.generate_snapshot(
                user=None, input_data=modified_input_data
            )

            self.assertNotEqual(first_snapshot.pk, third_snapshot.pk)
            self.assertEqual(CompletedAnswer.objects.count(), 2)

    def test_given_no_user_and_no_data_when_generate_snapshot_then_creates_empty_snapshot(
        self,
    ):
        completed_answer_snapshot = CompletedAnswer.objects.generate_snapshot(
            user=None, input_data=None
        )
        self.assertIsNone(completed_answer_snapshot.completed_by)
        self.assertEqual(
            completed_answer_snapshot.answers, {"conditioners": [], "axis": []}
        )
