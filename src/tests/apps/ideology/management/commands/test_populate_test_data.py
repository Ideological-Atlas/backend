from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from ideology.models import (
    IdeologyAbstractionComplexity,
    IdeologyAxis,
    IdeologyConditioner,
    IdeologyConditionerConditioner,
    IdeologySection,
    IdeologySectionConditioner,
)


class PopulateTestDataCommandTestCase(TestCase):
    @staticmethod
    def call_command(*args, **kwargs):
        standard_output = StringIO()
        call_command(
            "populate_test_data",
            *args,
            stdout=standard_output,
            stderr=StringIO(),
            **kwargs,
        )
        return standard_output.getvalue()

    def test_populate_test_data_creates_full_structure(self):
        command_output = self.call_command()

        self.assertIn("Test Level populated successfully", command_output)

        ideology_abstraction_complexity = IdeologyAbstractionComplexity.objects.filter(
            name_en="[TEST-EN] Test Level"
        ).first()
        self.assertIsNotNone(
            ideology_abstraction_complexity,
            "Ideology Abstraction Complexity Test Level was not created",
        )
        self.assertEqual(ideology_abstraction_complexity.complexity, 99)

        ideology_section_basic = IdeologySection.objects.get(
            name_en="[TEST-EN] Section 1 (Basic)",
            abstraction_complexity=ideology_abstraction_complexity,
        )
        self.assertEqual(
            ideology_section_basic.axes.count(),
            10,
            "Section 1 should have 10 questions",
        )
        self.assertFalse(
            ideology_section_basic.condition_rules.exists(),
            "Section 1 should not have conditions",
        )

        ideology_section_conditional = IdeologySection.objects.get(
            name_en="[TEST-EN] Section 2 (Cond A)"
        )

        self.assertTrue(
            IdeologySectionConditioner.objects.filter(
                section=ideology_section_conditional,
                conditioner__name_en="[TEST-EN] Conditioner A (Selector)",
            ).exists()
        )

        self.assertEqual(ideology_section_conditional.axes.count(), 10)

        ideology_axes_conditioned_by_b = IdeologyAxis.objects.filter(
            section=ideology_section_conditional,
            condition_rules__conditioner__name_en="[TEST-EN] Conditioner B",
        )
        self.assertEqual(
            ideology_axes_conditioned_by_b.count(),
            5,
            "There should be 5 questions conditioned by B in section 2",
        )

        ideology_section_complex = IdeologySection.objects.get(
            name_en="[TEST-EN] Section 3 (Complex)"
        )

        ideology_section_complex_conditions = IdeologySectionConditioner.objects.filter(
            section=ideology_section_complex
        )
        self.assertEqual(ideology_section_complex_conditions.count(), 2)
        conditioner_names = sorted(
            list(
                ideology_section_complex_conditions.values_list(
                    "conditioner__name_en", flat=True
                )
            )
        )
        self.assertIn("[TEST-EN] Conditioner C", conditioner_names)
        self.assertIn("[TEST-EN] Conditioner D (Nested)", conditioner_names)

        ideology_conditioner_d = IdeologyConditioner.objects.get(
            name_en="[TEST-EN] Conditioner D (Nested)"
        )
        ideology_conditioner_e = IdeologyConditioner.objects.get(
            name_en="[TEST-EN] Conditioner E (Root)"
        )
        self.assertTrue(
            IdeologyConditionerConditioner.objects.filter(
                target_conditioner=ideology_conditioner_d,
                source_conditioner=ideology_conditioner_e,
            ).exists(),
            "Conditioner D should depend on E",
        )

        self.assertEqual(ideology_section_complex.axes.count(), 10)

        ideology_conditioner_f = IdeologyConditioner.objects.get(
            name_en="[TEST-EN] Conditioner F"
        )
        ideology_axes_group_2 = IdeologyAxis.objects.filter(
            section=ideology_section_complex,
            condition_rules__conditioner=ideology_conditioner_f,
        )
        self.assertEqual(ideology_axes_group_2.count(), 3)
        for ideology_axis in ideology_axes_group_2:
            self.assertTrue(
                ideology_axis.conditioners.filter(
                    name_en="[TEST-EN] Conditioner G"
                ).exists()
            )

        ideology_conditioner_i = IdeologyConditioner.objects.get(
            name_en="[TEST-EN] Conditioner I (Nested)"
        )
        ideology_conditioner_j = IdeologyConditioner.objects.get(
            name_en="[TEST-EN] Conditioner J (Root)"
        )

        self.assertTrue(
            IdeologyConditionerConditioner.objects.filter(
                target_conditioner=ideology_conditioner_i,
                source_conditioner=ideology_conditioner_j,
            ).exists(),
            "Conditioner I should depend on J",
        )

        ideology_axes_group_3 = IdeologyAxis.objects.filter(
            section=ideology_section_complex,
            condition_rules__conditioner=ideology_conditioner_i,
        )
        self.assertEqual(ideology_axes_group_3.count(), 4)
        for ideology_axis in ideology_axes_group_3:
            self.assertTrue(
                ideology_axis.conditioners.filter(
                    name_en="[TEST-EN] Conditioner H"
                ).exists()
            )
