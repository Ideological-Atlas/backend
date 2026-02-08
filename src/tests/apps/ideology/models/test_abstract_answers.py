from core.factories import UserFactory
from django.core.exceptions import ValidationError
from django.test import TestCase
from ideology.factories import IdeologyAxisFactory, UserConditionerAnswerFactory
from ideology.models import UserAxisAnswer


class AbstractAnswerValidationTestCase(TestCase):
    def test_axis_answer_validation_missing_value(self):
        user = UserFactory()
        ideology_axis = IdeologyAxisFactory()
        user_axis_answer = UserAxisAnswer(
            user=user,
            axis=ideology_axis,
            is_indifferent=False,
            value=None,
        )
        with self.assertRaises(ValidationError) as validation_error:
            user_axis_answer.full_clean()
            self.assertIn(
                "A non-indifferent answer must have a numeric value",
                str(validation_error.exception),
            )

    def test_conditioner_answer_indifference_property(self):
        # Case 1: Explicit Indifference
        answer_indiff = UserConditionerAnswerFactory(answer="Indifferent")
        self.assertTrue(answer_indiff.is_indifferent_answer)

        # Case 2: Normal Answer
        answer_normal = UserConditionerAnswerFactory(answer="Option A")
        self.assertFalse(answer_normal.is_indifferent_answer)

        # Case 3: None/Empty Answer (Coverage missing branch)
        answer_none = UserConditionerAnswerFactory.build(answer=None)
        self.assertFalse(answer_none.is_indifferent_answer)

        answer_empty = UserConditionerAnswerFactory.build(answer="")
        self.assertFalse(answer_empty.is_indifferent_answer)
