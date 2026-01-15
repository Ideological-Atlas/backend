import uuid

from core.exceptions.api_exceptions import NotFoundException
from core.factories import UserFactory
from django.test import TestCase
from ideology.factories import IdeologyAxisFactory, IdeologyConditionerFactory
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

        data["value"] = 60
        answer, created = UserAxisAnswer.objects.upsert(self.user, self.axis.uuid, data)
        self.assertFalse(created)
        self.assertEqual(answer.value, 60)

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

        data["answer"] = "No"
        answer, created = UserConditionerAnswer.objects.upsert(
            self.user, self.conditioner.uuid, data
        )
        self.assertFalse(created)
        self.assertEqual(answer.answer, "No")

    def test_upsert_conditioner_answer_not_found(self):
        random_uuid = uuid.uuid4()
        with self.assertRaises(NotFoundException):
            UserConditionerAnswer.objects.upsert(self.user, random_uuid, {})
