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

    def test_generate_snapshot_from_db_user(self):
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

    def test_generate_snapshot_creates_hash(self):
        ideology_axis = IdeologyAxisFactory()
        UserAxisAnswerFactory(user=self.user, axis=ideology_axis, value=50)

        completed_answer_snapshot = CompletedAnswer.objects.generate_snapshot(
            user=self.user
        )

        self.assertIsNotNone(completed_answer_snapshot.answer_hash)
        self.assertEqual(len(completed_answer_snapshot.answer_hash), 64)

    def test_generate_snapshot_avoids_duplicates_using_hash(self):
        ideology_axis = IdeologyAxisFactory()
        UserAxisAnswerFactory(user=self.user, axis=ideology_axis, value=50)

        first_completed_answer_snapshot = CompletedAnswer.objects.generate_snapshot(
            user=self.user
        )

        with self.subTest("Should return existing instance for identical data"):
            second_completed_answer_snapshot = (
                CompletedAnswer.objects.generate_snapshot(user=self.user)
            )

            self.assertEqual(
                first_completed_answer_snapshot.pk,
                second_completed_answer_snapshot.pk,
            )
            self.assertEqual(
                first_completed_answer_snapshot.answer_hash,
                second_completed_answer_snapshot.answer_hash,
            )
            self.assertEqual(CompletedAnswer.objects.count(), 1)

        with self.subTest("Should create new instance for modified data"):
            UserAxisAnswerFactory(user=self.user, axis=IdeologyAxisFactory(), value=10)

            third_completed_answer_snapshot = CompletedAnswer.objects.generate_snapshot(
                user=self.user
            )

            self.assertNotEqual(
                first_completed_answer_snapshot.pk, third_completed_answer_snapshot.pk
            )
            self.assertNotEqual(
                first_completed_answer_snapshot.answer_hash,
                third_completed_answer_snapshot.answer_hash,
            )
            self.assertEqual(CompletedAnswer.objects.count(), 2)

    def test_generate_snapshot_from_raw_data_anonymous(self):
        raw_answers_data = {
            "axis": [
                {
                    "uuid": "11111111111111111111111111111111",
                    "value": 10,
                    "margin_left": 0,
                    "margin_right": 0,
                }
            ],
            "conditioners": [
                {"uuid": "22222222222222222222222222222222", "value": "Option_A"}
            ],
        }

        completed_answer_snapshot = CompletedAnswer.objects.generate_snapshot(
            user=None, data=raw_answers_data
        )

        self.assertIsNone(completed_answer_snapshot.completed_by)
        self.assertEqual(completed_answer_snapshot.answers, raw_answers_data)

    def test_generate_snapshot_anonymous_deduplication(self):
        raw_answers_data = {
            "axis": [{"uuid": "a" * 32, "value": 10}],
            "conditioners": [],
        }

        with self.subTest("Should return existing instance for identical data"):
            first_anonymous_snapshot = CompletedAnswer.objects.generate_snapshot(
                user=None, data=raw_answers_data
            )
            second_anonymous_snapshot = CompletedAnswer.objects.generate_snapshot(
                user=None, data=raw_answers_data
            )

            self.assertEqual(first_anonymous_snapshot.pk, second_anonymous_snapshot.pk)
            self.assertEqual(
                first_anonymous_snapshot.answer_hash,
                second_anonymous_snapshot.answer_hash,
            )
            self.assertEqual(CompletedAnswer.objects.count(), 1)

        with self.subTest("Should create new instance for modified data"):
            modified_answers_data = {
                "axis": [{"uuid": "b" * 32, "value": 20}],
                "conditioners": [],
            }
            third_anonymous_snapshot = CompletedAnswer.objects.generate_snapshot(
                user=None, data=modified_answers_data
            )

            self.assertNotEqual(
                first_anonymous_snapshot.pk, third_anonymous_snapshot.pk
            )
            self.assertEqual(CompletedAnswer.objects.count(), 2)

    def test_generate_snapshot_no_user_no_data(self):
        completed_answer_snapshot = CompletedAnswer.objects.generate_snapshot(
            user=None, data=None
        )
        self.assertIsNone(completed_answer_snapshot.completed_by)
        self.assertEqual(
            completed_answer_snapshot.answers, {"conditioners": [], "axis": []}
        )
