from typing import cast

from core.factories import UserFactory
from core.services.affinity_calculator import AffinityCalculator
from django.test import TestCase
from ideology.factories import (
    IdeologyAbstractionComplexityFactory,
    IdeologyAxisFactory,
    IdeologySectionFactory,
    UserAxisAnswerFactory,
)
from ideology.models import UserAxisAnswer
from ideology.services.calculation_dto import CalculationItem


class AffinityCalculatorTestCase(TestCase):
    def setUp(self):
        self.user_a = UserFactory()
        self.user_b = UserFactory()
        self.comp_1 = IdeologyAbstractionComplexityFactory(complexity=1)
        self.section_1 = IdeologySectionFactory(abstraction_complexity=self.comp_1)
        self.axis_1 = IdeologyAxisFactory(section=self.section_1)
        self.axis_2 = IdeologyAxisFactory(section=self.section_1)

    @staticmethod
    def _get_data(user):
        return UserAxisAnswer.objects.get_mapped_for_calculation(user)

    def test_calculate_unmatched_axes_return_null(self):
        UserAxisAnswerFactory(user=self.user_a, axis=self.axis_1, value=50)
        UserAxisAnswerFactory(user=self.user_b, axis=self.axis_2, value=50)

        calculator = AffinityCalculator(
            self._get_data(self.user_a), self._get_data(self.user_b)
        )
        result = calculator.calculate_detailed()

        self.assertIsNone(result["total"])
        comp_res = result["complexities"][0]
        self.assertIsNone(comp_res["affinity"])

    def test_calculate_partial_overlap_union(self):
        UserAxisAnswerFactory(user=self.user_a, axis=self.axis_1, value=10)
        UserAxisAnswerFactory(user=self.user_b, axis=self.axis_1, value=10)
        UserAxisAnswerFactory(user=self.user_a, axis=self.axis_2, value=10)

        calculator = AffinityCalculator(
            self._get_data(self.user_a), self._get_data(self.user_b)
        )
        result = calculator.calculate_detailed()

        self.assertEqual(result["total"], 100.0)

    def test_empty_users(self):
        calculator = AffinityCalculator({}, {})
        result = calculator.calculate_detailed()
        self.assertIsNone(result["total"])

    def test_mutual_indifference(self):
        UserAxisAnswerFactory(user=self.user_a, axis=self.axis_1, is_indifferent=True)
        UserAxisAnswerFactory(user=self.user_b, axis=self.axis_1, is_indifferent=True)

        calc = AffinityCalculator(
            self._get_data(self.user_a), self._get_data(self.user_b)
        )
        result = calc.calculate_detailed()
        self.assertEqual(result["total"], 100.0)

    def test_one_sided_indifference(self):
        UserAxisAnswerFactory(user=self.user_a, axis=self.axis_1, value=50)
        UserAxisAnswerFactory(user=self.user_b, axis=self.axis_1, is_indifferent=True)

        calc = AffinityCalculator(
            self._get_data(self.user_a), self._get_data(self.user_b)
        )
        result = calc.calculate_detailed()
        self.assertEqual(result["total"], 75.0)

    def test_gap_logic_min2_greater_max1(self):
        UserAxisAnswerFactory(
            user=self.user_a, axis=self.axis_1, value=10, margin_left=0, margin_right=0
        )
        UserAxisAnswerFactory(
            user=self.user_b, axis=self.axis_1, value=40, margin_left=0, margin_right=0
        )

        calc = AffinityCalculator(
            self._get_data(self.user_a), self._get_data(self.user_b)
        )
        result = calc.calculate_detailed()
        self.assertEqual(result["total"], 36.12)

    def test_gap_logic_min1_greater_max2(self):
        UserAxisAnswerFactory(
            user=self.user_a, axis=self.axis_1, value=40, margin_left=0, margin_right=0
        )
        UserAxisAnswerFactory(
            user=self.user_b, axis=self.axis_1, value=10, margin_left=0, margin_right=0
        )

        calc = AffinityCalculator(
            self._get_data(self.user_a), self._get_data(self.user_b)
        )
        result = calc.calculate_detailed()
        self.assertEqual(result["total"], 36.12)

    def test_contact_distance_logic_v1_less_than_v2(self):
        UserAxisAnswerFactory(
            user=self.user_a, axis=self.axis_1, value=10, margin_left=5, margin_right=5
        )
        UserAxisAnswerFactory(
            user=self.user_b, axis=self.axis_1, value=14, margin_left=5, margin_right=5
        )

        calc = AffinityCalculator(
            self._get_data(self.user_a), self._get_data(self.user_b)
        )
        result = calc.calculate_detailed()
        self.assertEqual(result["total"], 68.0)

    def test_contact_distance_logic_v1_greater_v2(self):
        UserAxisAnswerFactory(
            user=self.user_a, axis=self.axis_1, value=20, margin_left=5, margin_right=5
        )
        UserAxisAnswerFactory(
            user=self.user_b, axis=self.axis_1, value=15, margin_left=5, margin_right=5
        )

        calc = AffinityCalculator(
            self._get_data(self.user_a), self._get_data(self.user_b)
        )
        result = calc.calculate_detailed()
        self.assertEqual(result["total"], 62.5)

    def test_defensive_missing_complexity_or_item(self):
        data_a = {"bad_key": None}
        data_b = {
            "no_complexity": CalculationItem(
                type="axis", value=50, complexity_uuid=None
            )
        }

        calc = AffinityCalculator(cast(dict[str, CalculationItem], data_a), data_b)
        result = calc.calculate_detailed()
        self.assertIsNone(result["total"])

    def test_quadratic_affinity_perfect_match(self):
        UserAxisAnswerFactory(
            user=self.user_a, axis=self.axis_1, value=50, margin_left=0, margin_right=0
        )
        UserAxisAnswerFactory(
            user=self.user_b, axis=self.axis_1, value=50, margin_left=0, margin_right=0
        )
        calc = AffinityCalculator(
            self._get_data(self.user_a), self._get_data(self.user_b)
        )
        result = calc.calculate_detailed()
        self.assertEqual(result["total"], 100.0)

    def test_quadratic_affinity_large_gap_zero_score(self):
        UserAxisAnswerFactory(
            user=self.user_a,
            axis=self.axis_1,
            value=-100,
            margin_left=0,
            margin_right=0,
        )
        UserAxisAnswerFactory(
            user=self.user_b, axis=self.axis_1, value=100, margin_left=0, margin_right=0
        )
        calc = AffinityCalculator(
            self._get_data(self.user_a), self._get_data(self.user_b)
        )
        result = calc.calculate_detailed()
        self.assertEqual(result["total"], 0.0)

    def test_orphaned_axis_no_section(self):
        data_a = {
            "axis_no_section": CalculationItem(
                type="axis", value=50, complexity_uuid="comp1", section_uuid=None
            )
        }
        calc = AffinityCalculator(data_a, {})
        result = calc.calculate_detailed()
        self.assertIn("complexities", result)
        self.assertEqual(len(result["complexities"][0]["sections"]), 0)

    def test_conditioner_scoring_mechanics_and_missing_keys(self):
        cid = "c_uuid"
        sid = "s_uuid"

        data_a = {
            "base_axis": CalculationItem(
                type="axis",
                value=50,
                is_indifferent=True,
                complexity_uuid=cid,
                section_uuid=sid,
            ),
            "cond_match": CalculationItem(
                type="conditioner", value="yes", complexity_uuid=cid
            ),
            "cond_mismatch": CalculationItem(
                type="conditioner", value="yes", complexity_uuid=cid
            ),
            "cond_indiff": CalculationItem(
                type="conditioner",
                value="yes",
                is_indifferent=True,
                complexity_uuid=cid,
            ),
            "cond_missing_in_b": CalculationItem(
                type="conditioner", value="yes", complexity_uuid=cid
            ),
        }

        data_b = {
            "base_axis": CalculationItem(
                type="axis", value=50, complexity_uuid=cid, section_uuid=sid
            ),
            "cond_match": CalculationItem(
                type="conditioner", value="yes", complexity_uuid=cid
            ),
            "cond_mismatch": CalculationItem(
                type="conditioner", value="no", complexity_uuid=cid
            ),
            "cond_indiff": CalculationItem(
                type="conditioner", value="yes", complexity_uuid=cid
            ),
        }

        calc = AffinityCalculator(data_a, data_b)
        result = calc.calculate_detailed()

        complexity_res = result["complexities"][0]
        base_affinity = complexity_res["base_affinity"]
        modifier = complexity_res["conditioner_modifier"]

        self.assertEqual(base_affinity, 75.0)

        expected_modifier = 5.0 - 5.0 + 2.5
        self.assertEqual(modifier, expected_modifier)
        self.assertEqual(result["total"], 75.0 + expected_modifier)
