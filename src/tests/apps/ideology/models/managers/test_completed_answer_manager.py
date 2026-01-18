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
        axis = IdeologyAxisFactory()
        conditioner = IdeologyConditionerFactory()

        UserAxisAnswerFactory(
            user=self.user, axis=axis, value=50, margin_left=5, margin_right=5
        )
        UserConditionerAnswerFactory(
            user=self.user, conditioner=conditioner, answer="Yes"
        )

        snapshot = CompletedAnswer.objects.generate_snapshot(user=self.user)

        self.assertEqual(snapshot.completed_by, self.user)
        data = snapshot.answers

        self.assertIn("axis", data)
        self.assertIn("conditioners", data)

        self.assertEqual(len(data["axis"]), 1)
        self.assertEqual(data["axis"][0]["uuid"], axis.uuid.hex)
        self.assertEqual(data["axis"][0]["value"], 50)

        self.assertEqual(len(data["conditioners"]), 1)
        self.assertEqual(data["conditioners"][0]["uuid"], conditioner.uuid.hex)
        self.assertEqual(data["conditioners"][0]["value"], "Yes")

    def test_generate_snapshot_from_raw_data_anonymous(self):
        raw_data = {
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

        snapshot = CompletedAnswer.objects.generate_snapshot(user=None, data=raw_data)

        self.assertIsNone(snapshot.completed_by)
        self.assertEqual(snapshot.answers, raw_data)

    def test_generate_snapshot_no_user_no_data(self):
        snapshot = CompletedAnswer.objects.generate_snapshot(user=None, data=None)
        self.assertIsNone(snapshot.completed_by)
        expected_default: dict = {"conditioners": [], "axis": []}
        self.assertEqual(snapshot.answers, expected_default)
