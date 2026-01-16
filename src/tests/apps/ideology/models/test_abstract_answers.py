from core.factories import UserFactory
from django.core.exceptions import ValidationError
from django.test import TestCase
from ideology.factories import IdeologyAxisFactory
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
