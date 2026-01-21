import uuid

from core.exceptions.api_exceptions import NotFoundException
from core.factories import UserFactory
from django.test import TestCase
from ideology.factories import (
    IdeologyAxisFactory,
    IdeologyConditionerFactory,
    UserAxisAnswerFactory,
)
from ideology.models import UserAxisAnswer, UserConditionerAnswer


class UserAnswersManagerTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.axis = IdeologyAxisFactory()
        self.conditioner = IdeologyConditionerFactory()

    def test_upsert_axis_answer_success(self):
        data = {
            "value": 50,
            "margin_left": 5,
            "margin_right": 5,
            "is_indifferent": False,
        }
        answer, created = UserAxisAnswer.objects.upsert(self.user, self.axis.uuid, data)
        self.assertTrue(created)
        self.assertEqual(answer.value, 50)

    def test_upsert_axis_answer_not_found(self):
        random_uuid = uuid.uuid4()
        with self.assertRaises(NotFoundException):
            UserAxisAnswer.objects.upsert(self.user, random_uuid, {})

    def test_upsert_conditioner_answer_success(self):
        data = {"answer": "Yes"}
        answer, created = UserConditionerAnswer.objects.upsert(
            self.user, self.conditioner.uuid, data
        )
        self.assertTrue(created)
        self.assertEqual(answer.answer, "Yes")

    def test_upsert_conditioner_answer_not_found(self):
        random_uuid = uuid.uuid4()
        with self.assertRaises(NotFoundException):
            UserConditionerAnswer.objects.upsert(self.user, random_uuid, {})

    def test_get_mapped_for_calculation(self):
        # Setup: 1 normal answer, 1 indifferent, 1 None value
        axis_1 = IdeologyAxisFactory()
        axis_2 = IdeologyAxisFactory()
        axis_3 = IdeologyAxisFactory()

        # Valid answer
        UserAxisAnswerFactory(
            user=self.user,
            axis=axis_1,
            value=10,
            margin_left=5,
            margin_right=5,
            is_indifferent=False,
        )
        # Indifferent answer (Should be ignored)
        UserAxisAnswerFactory(user=self.user, axis=axis_2, is_indifferent=True)
        # Missing value (Should be ignored, though usually prevented by model)
        UserAxisAnswerFactory(
            user=self.user, axis=axis_3, value=None, is_indifferent=False
        )

        result = UserAxisAnswer.objects.get_mapped_for_calculation(self.user)

        self.assertIn(str(axis_1.uuid.hex), result)
        self.assertNotIn(str(axis_2.uuid.hex), result)
        self.assertNotIn(str(axis_3.uuid.hex), result)

        entry = result[str(axis_1.uuid.hex)]
        self.assertEqual(entry["value"], 10)
        self.assertEqual(entry["margin_left"], 5)
