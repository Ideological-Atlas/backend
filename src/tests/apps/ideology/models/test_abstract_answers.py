from core.factories import UserFactory
from django.core.exceptions import ValidationError
from django.test import TestCase
from ideology.factories import IdeologyAxisFactory
from ideology.models import UserAxisAnswer


class AbstractAnswerValidationTestCase(TestCase):
    def test_axis_answer_validation_missing_value(self):
        user = UserFactory()
        axis = IdeologyAxisFactory()
        answer = UserAxisAnswer(user=user, axis=axis, is_indifferent=False, value=None)
        with self.assertRaises(ValidationError) as cm:
            answer.full_clean()
            self.assertIn(
                "A non-indifferent answer must have a numeric value", str(cm.exception)
            )
