from core.factories import UserFactory
from django.core.exceptions import ValidationError
from django.db import IntegrityError, InternalError, transaction
from django.test import TestCase
from django.utils import translation
from ideology.factories import AxisAnswerFactory, IdeologyAxisFactory, IdeologyFactory
from ideology.models import AxisAnswer


class AxisAnswerModelTestCase(TestCase):
    def test_str_representations(self):
        user = UserFactory(username="u1")
        ideology = IdeologyFactory(name="I1")
        axis = IdeologyAxisFactory(name="A1")

        axis_answer_user = AxisAnswerFactory(
            user=user, ideology=None, axis=axis, value=50
        )
        axis_answer_ideology = AxisAnswerFactory(
            trait_ideology=True, ideology=ideology, axis=axis, value=-50
        )

        self.assertEqual(str(axis_answer_user), "A1: 50 (u1)")
        self.assertEqual(str(axis_answer_ideology), "A1: -50 (I1)")

    def test_margin_bounds_validation_clean_invalid(self):
        axis = IdeologyAxisFactory()

        test_cases = [
            {
                "msg": "Lower bound error (-90 - 20 < -100)",
                "value": -90,
                "margin_left": 20,
                "margin_right": 0,
                "error_text": "Lower bound error",
            },
            {
                "msg": "Upper bound error (80 + 30 > 100)",
                "value": 80,
                "margin_left": 0,
                "margin_right": 30,
                "error_text": "Upper bound error",
            },
        ]

        with translation.override("en"):
            for case in test_cases:
                with self.subTest(msg=case["msg"]):
                    with self.assertRaises(ValidationError) as context_manager:
                        AxisAnswerFactory(
                            axis=axis,
                            value=case["value"],
                            margin_left=case["margin_left"],
                            margin_right=case["margin_right"],
                        )
                    self.assertIn(case["error_text"], str(context_manager.exception))

    def test_margin_bounds_validation_clean_valid(self):
        axis = IdeologyAxisFactory()

        test_cases = [
            {
                "msg": "Valid lower boundary (-80 - 20 = -100)",
                "value": -80,
                "margin_left": 20,
                "margin_right": 0,
            },
            {
                "msg": "Valid upper boundary (50 + 50 = 100)",
                "value": 50,
                "margin_left": 0,
                "margin_right": 50,
            },
        ]

        for case in test_cases:
            with self.subTest(msg=case["msg"]):
                AxisAnswerFactory(
                    axis=axis,
                    value=case["value"],
                    margin_left=case["margin_left"],
                    margin_right=case["margin_right"],
                )

    def test_db_constraints(self):
        axis_answer = AxisAnswerFactory(value=0, margin_left=0)

        test_cases = [
            {
                "msg": "Lower bound constraint violation",
                "update_data": {
                    "value": -100,
                    "margin_left": 10,
                },
            },
            {
                "msg": "Upper bound constraint violation",
                "update_data": {
                    "value": 90,
                    "margin_right": 20,
                },
            },
        ]

        for case in test_cases:
            with self.subTest(msg=case["msg"]):
                with self.assertRaises((IntegrityError, InternalError)):
                    with transaction.atomic():
                        AxisAnswer.objects.filter(pk=axis_answer.pk).update(
                            **case["update_data"]
                        )

    def test_clean_coverage_edge_cases(self):
        axis = IdeologyAxisFactory()

        answer_none_value = AxisAnswerFactory.build(axis=axis, value=None)
        try:
            answer_none_value.clean()
        except Exception as e:
            self.fail(f"clean() fallo con value=None: {e}")

        answer_none_margin_left = AxisAnswerFactory.build(
            axis=axis, value=50, margin_left=None
        )
        try:
            answer_none_margin_left.clean()
        except Exception as e:
            self.fail(f"clean() fallo con margin_left=None: {e}")

        answer_none_margin_right = AxisAnswerFactory.build(
            axis=axis, value=50, margin_right=None
        )
        try:
            answer_none_margin_right.clean()
        except Exception as e:
            self.fail(f"clean() fallo con margin_right=None: {e}")
