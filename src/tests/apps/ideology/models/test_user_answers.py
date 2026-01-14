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
        axis = IdeologyAxisFactory(name="Economic")
        answer = UserAxisAnswerFactory(user=user, axis=axis, value=50)
        self.assertEqual(str(answer), "tester - Economic: 50")

    def test_indifference(self):
        user = UserFactory(username="indifferent_user")
        axis = IdeologyAxisFactory(name="Social")
        answer = UserAxisAnswerFactory(user=user, axis=axis, is_indifferent=True)
        self.assertEqual(str(answer), "indifferent_user - Social: Indifferent")
        self.assertIsNone(answer.value)


class UserConditionerAnswerModelTestCase(TestCase):
    def test_str_representation(self):
        user = UserFactory(username="u1")
        cond = IdeologyConditionerFactory(name="C1")
        answer = UserConditionerAnswerFactory(user=user, conditioner=cond, answer="Yes")
        self.assertEqual(str(answer), "u1 - C1: Yes")
