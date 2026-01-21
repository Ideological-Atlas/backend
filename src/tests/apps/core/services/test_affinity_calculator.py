from core.factories import UserFactory
from core.services.affinity_calculator import AffinityCalculator
from django.test import TestCase
from ideology.factories import (
    IdeologyAbstractionComplexityFactory,
    IdeologyAxisFactory,
    IdeologySectionFactory,
    UserAxisAnswerFactory,
)


class AffinityCalculatorTestCase(TestCase):
    def setUp(self):
        self.user_a = UserFactory()
        self.user_b = UserFactory()
        self.comp_1 = IdeologyAbstractionComplexityFactory(complexity=1)
        self.section_1 = IdeologySectionFactory(abstraction_complexity=self.comp_1)
        self.axis_1 = IdeologyAxisFactory(section=self.section_1)

    def test_calculate_grouped_by_complexity(self):
        # Perfect Match (100)
        UserAxisAnswerFactory(user=self.user_a, axis=self.axis_1, value=50)
        UserAxisAnswerFactory(user=self.user_b, axis=self.axis_1, value=50)

        calculator = AffinityCalculator(self.user_a, self.user_b)
        result = calculator.calculate_detailed()

        self.assertEqual(result["total"], 100.0)
        self.assertEqual(len(result["complexities"]), 1)

        # Structure check
        comp_res = result["complexities"][0]
        self.assertEqual(comp_res["complexity_uuid"], self.comp_1.uuid.hex)
        self.assertEqual(comp_res["affinity"], 100.0)

    def test_partial_indifference(self):
        """
        User A is indifferent. User B has a value.
        Should result in PARTIAL_INDIFFERENCE_SCORE (75.0).
        """
        UserAxisAnswerFactory(user=self.user_a, axis=self.axis_1, is_indifferent=True)
        UserAxisAnswerFactory(
            user=self.user_b, axis=self.axis_1, value=50, is_indifferent=False
        )

        calculator = AffinityCalculator(self.user_a, self.user_b)
        result = calculator.calculate_detailed()

        # Expect 75.0
        self.assertEqual(result["total"], 75.0)

        # Verify in breakdown
        axes_breakdown = result["complexities"][0]["sections"][0]["axes"]
        self.assertEqual(axes_breakdown[0]["affinity"], 75.0)
        self.assertTrue(axes_breakdown[0]["user_a"]["is_indifferent"])

    def test_both_indifferent(self):
        """
        Both users indifferent.
        Logic: They agree on not caring -> Perfect Match (100.0).
        """
        UserAxisAnswerFactory(user=self.user_a, axis=self.axis_1, is_indifferent=True)
        UserAxisAnswerFactory(user=self.user_b, axis=self.axis_1, is_indifferent=True)

        calculator = AffinityCalculator(self.user_a, self.user_b)
        self.assertEqual(calculator.calculate_detailed()["total"], 100.0)

    def test_empty_users(self):
        calculator = AffinityCalculator(self.user_a, self.user_b)
        result = calculator.calculate_detailed()
        self.assertEqual(result["total"], 50.0)
        self.assertEqual(len(result["complexities"]), 0)
