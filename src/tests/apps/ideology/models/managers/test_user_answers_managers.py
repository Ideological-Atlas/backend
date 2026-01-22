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
        axis_1 = IdeologyAxisFactory()
        axis_2 = IdeologyAxisFactory()
        axis_3 = IdeologyAxisFactory()

        UserAxisAnswerFactory(
            user=self.user,
            axis=axis_1,
            value=10,
            margin_left=5,
            margin_right=5,
            is_indifferent=False,
        )
        UserAxisAnswerFactory(user=self.user, axis=axis_2, is_indifferent=True)

        bad_answer = UserAxisAnswerFactory.build(
            user=self.user, axis=axis_3, value=None, is_indifferent=False
        )
        UserAxisAnswer.objects.bulk_create([bad_answer])

        result = UserAxisAnswer.objects.get_mapped_for_calculation(self.user)

        self.assertIn(str(axis_1.uuid.hex), result)

        self.assertIn(str(axis_2.uuid.hex), result)
        self.assertTrue(result[str(axis_2.uuid.hex)]["is_indifferent"])

        self.assertNotIn(str(axis_3.uuid.hex), result)

        entry = result[str(axis_1.uuid.hex)]
        self.assertEqual(entry["value"], 10)
        self.assertEqual(entry["margin_left"], 5)
