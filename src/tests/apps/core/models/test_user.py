import random
from unittest.mock import patch

from core.exceptions.user_exceptions import UserAlreadyVerifiedException
from core.factories import UserFactory
from django.test import TestCase


class UserModelTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_verify_user_flow(self):
        self.assertFalse(self.user.is_verified)
        self.user.verify()
        self.assertTrue(self.user.is_verified)

        with self.assertRaises(UserAlreadyVerifiedException):
            self.user.verify()

    def test_str_representation(self):
        self.assertEqual(str(self.user), self.user.username)

    @patch("core.tasks.send_email_notification.delay")
    def test_trigger_email_verification(self, mock_send):
        self.user.trigger_email_verification(language="en")
        mock_send.assert_called_once()

        mock_send.reset_mock()
        self.user.is_verified = True
        self.user.trigger_email_verification()
        mock_send.assert_not_called()

    def test_generate_completed_answer_structure_randomized(self):
        from ideology.factories import (
            AxisAnswerFactory,
            ConditionerAnswerFactory,
            IdeologyAbstractionComplexityFactory,
            IdeologyAxisFactory,
            IdeologyConditionerFactory,
            IdeologySectionFactory,
        )

        number_of_complexities = random.randint(2, 4)  # nosec
        complexities = []
        for complexity_index in range(number_of_complexities):
            complexities.append(
                IdeologyAbstractionComplexityFactory(
                    complexity=complexity_index + 1,
                    name=f"Complexity-{complexity_index+1}",
                )
            )

        for complexity in complexities:
            level = complexity.complexity

            number_of_sections = random.randint(5, 10)  # nosec
            sections = []
            for section_index in range(number_of_sections):
                sections.append(
                    IdeologySectionFactory(
                        name=f"Sec-{level}-{section_index}",
                        abstraction_complexity=complexity,
                        add_axes__total=0,
                    )
                )

            for section in sections:
                number_of_axes = random.randint(10, 15)  # nosec
                for axis_index in range(number_of_axes):
                    axis = IdeologyAxisFactory(
                        section=section, name=f"Axis-{section.name}-{axis_index}"
                    )
                    AxisAnswerFactory(user=self.user, axis=axis, value=0.5)

            if level >= 2:
                number_of_conditioners = random.randint(5, 10)  # nosec
                for conditioner_index in range(number_of_conditioners):
                    cond = IdeologyConditionerFactory(
                        abstraction_complexity=complexity,
                        name=f"Cond-{level}-{conditioner_index}",
                    )
                    ConditionerAnswerFactory(
                        user=self.user, conditioner=cond, answer="Yes"
                    )

        completed = self.user.generate_completed_answer()
        data = completed.answers

        self.assertEqual(completed.completed_by, self.user)
        self.assertEqual(len(data), number_of_complexities)

        for completed_answer in data:
            current_level = completed_answer["complexity"]

            self.assertTrue(
                5 <= len(completed_answer["sections"]) <= 10,
                f"Level {current_level} has {len(completed_answer['sections'])} sections, expected 5-10",
            )

            for section_data in completed_answer["sections"]:
                number_of_axes_found = len(section_data["axes"])
                self.assertTrue(
                    10 <= number_of_axes_found <= 15,
                    f"Section {section_data['name']} has {number_of_axes_found} axes, expected 10-15",
                )

            number_of_conditions_found = len(completed_answer["conditioners"])
            if current_level < 2:
                self.assertEqual(
                    number_of_conditions_found,
                    0,
                    f"Level {current_level} should have 0 conditioners, found {number_of_conditions_found}",
                )
            else:
                self.assertTrue(
                    5 <= number_of_conditions_found <= 10,
                    f"Level {current_level} has {number_of_conditions_found} conditioners, expected 5-10",
                )
