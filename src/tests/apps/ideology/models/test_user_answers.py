from core.factories import UserFactory
from django.test import TestCase
from ideology.factories import (
    IdeologyAxisFactory,
    IdeologyConditionerFactory,
    UserAxisAnswerFactory,
    UserConditionerAnswerFactory,
)


class UserAxisAnswerModelTestCase(TestCase):
    def test_str_representation(self):
        user = UserFactory(username="tester")
        ideology_axis = IdeologyAxisFactory(name="Economic")
        user_axis_answer = UserAxisAnswerFactory(
            user=user, axis=ideology_axis, value=50
        )
        self.assertEqual(str(user_axis_answer), "tester - Economic: 50")

    def test_indifference(self):
        user = UserFactory(username="indifferent_user")
        ideology_axis = IdeologyAxisFactory(name="Social")
        user_axis_answer = UserAxisAnswerFactory(
            user=user, axis=ideology_axis, is_indifferent=True
        )
        self.assertEqual(
            str(user_axis_answer), "indifferent_user - Social: Indifferent"
        )
        self.assertIsNone(user_axis_answer.value)


class UserConditionerAnswerModelTestCase(TestCase):
    def test_str_representation(self):
        user = UserFactory(username="user_1")
        ideology_conditioner = IdeologyConditionerFactory(name="Conditioner_1")
        user_conditioner_answer = UserConditionerAnswerFactory(
            user=user, conditioner=ideology_conditioner, answer="Yes"
        )
        self.assertEqual(str(user_conditioner_answer), "user_1 - Conditioner_1: Yes")
