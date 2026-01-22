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


class AffinityCalculatorTestCase(TestCase):
    def setUp(self):
        self.user_a = UserFactory()
        self.user_b = UserFactory()
        self.comp_1 = IdeologyAbstractionComplexityFactory(complexity=1)
        self.section_1 = IdeologySectionFactory(abstraction_complexity=self.comp_1)
        self.axis_1 = IdeologyAxisFactory(section=self.section_1)
        self.axis_2 = IdeologyAxisFactory(section=self.section_1)

    def _get_data(self, user):
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

        sec_res = comp_res["sections"][0]
        self.assertEqual(len(sec_res["axes"]), 2)

        for ax in sec_res["axes"]:
            self.assertIsNone(ax["affinity"])
            self.assertTrue(ax["user_a"] or ax["user_b"])

    def test_calculate_partial_overlap_union(self):
        UserAxisAnswerFactory(user=self.user_a, axis=self.axis_1, value=10)
        UserAxisAnswerFactory(user=self.user_b, axis=self.axis_1, value=10)

        UserAxisAnswerFactory(user=self.user_a, axis=self.axis_2, value=10)

        calculator = AffinityCalculator(
            self._get_data(self.user_a), self._get_data(self.user_b)
        )
        result = calculator.calculate_detailed()

        self.assertEqual(result["total"], 100.0)

        sec_axes = result["complexities"][0]["sections"][0]["axes"]
        self.assertEqual(len(sec_axes), 2)

        shared = next(
            a for a in sec_axes if a["axis_uuid"] == str(self.axis_1.uuid.hex)
        )
        self.assertEqual(shared["affinity"], 100.0)
        self.assertIsNotNone(shared["user_a"])
        self.assertIsNotNone(shared["user_b"])

        unmatched = next(
            a for a in sec_axes if a["axis_uuid"] == str(self.axis_2.uuid.hex)
        )
        self.assertIsNone(unmatched["affinity"])
        self.assertIsNotNone(unmatched["user_a"])
        self.assertIsNone(unmatched["user_b"])

    def test_empty_users(self):
        calculator = AffinityCalculator({}, {})
        result = calculator.calculate_detailed()
        self.assertIsNone(result["total"])
