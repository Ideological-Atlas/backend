from django.test import TestCase
from ideology.factories import (
    IdeologyAbstractionComplexityFactory,
    IdeologyAxisConditionerFactory,
    IdeologyAxisFactory,
    IdeologyConditionerConditionerFactory,
    IdeologyConditionerFactory,
    IdeologySectionConditionerFactory,
    IdeologySectionFactory,
)
from ideology.models import IdeologyConditioner


class IdeologyConditionerManagerTestCase(TestCase):
    def setUp(self):
        self.ideology_abstraction_complexity = IdeologyAbstractionComplexityFactory()

    def test_get_by_complexity_empty(self):
        queryset = IdeologyConditioner.objects.get_by_complexity(
            self.ideology_abstraction_complexity.uuid
        )
        self.assertFalse(queryset.exists())

    def test_get_by_complexity_direct_rules(self):
        with self.subTest("Section Rule"):
            ideology_section = IdeologySectionFactory(
                abstraction_complexity=self.ideology_abstraction_complexity
            )
            ideology_conditioner_section = IdeologyConditionerFactory()
            IdeologySectionConditionerFactory(
                section=ideology_section, conditioner=ideology_conditioner_section
            )

            queryset = IdeologyConditioner.objects.get_by_complexity(
                self.ideology_abstraction_complexity.uuid
            )
            self.assertIn(ideology_conditioner_section, queryset)

        with self.subTest("Axis Rule"):
            ideology_section_axis = IdeologySectionFactory(
                abstraction_complexity=self.ideology_abstraction_complexity
            )
            ideology_axis = IdeologyAxisFactory(section=ideology_section_axis)
            ideology_conditioner_axis = IdeologyConditionerFactory()
            IdeologyAxisConditionerFactory(
                axis=ideology_axis, conditioner=ideology_conditioner_axis
            )

            queryset = IdeologyConditioner.objects.get_by_complexity(
                self.ideology_abstraction_complexity.uuid
            )
            self.assertIn(ideology_conditioner_axis, queryset)

    def test_get_by_complexity_recursive_chain(self):
        ideology_section = IdeologySectionFactory(
            abstraction_complexity=self.ideology_abstraction_complexity
        )
        ideology_conditioner_root = IdeologyConditionerFactory(name="C")
        ideology_conditioner_mid = IdeologyConditionerFactory(name="B")
        ideology_conditioner_top = IdeologyConditionerFactory(name="A")

        IdeologySectionConditionerFactory(
            section=ideology_section, conditioner=ideology_conditioner_top
        )

        IdeologyConditionerConditionerFactory(
            target_conditioner=ideology_conditioner_top,
            conditioner=ideology_conditioner_mid,
        )

        IdeologyConditionerConditionerFactory(
            target_conditioner=ideology_conditioner_mid,
            conditioner=ideology_conditioner_root,
        )

        queryset = IdeologyConditioner.objects.get_by_complexity(
            self.ideology_abstraction_complexity.uuid
        )

        self.assertEqual(queryset.count(), 3)
        self.assertIn(ideology_conditioner_top, queryset)
        self.assertIn(ideology_conditioner_mid, queryset)
        self.assertIn(ideology_conditioner_root, queryset)

    def test_get_by_complexity_circular_dependency_safe(self):
        ideology_section = IdeologySectionFactory(
            abstraction_complexity=self.ideology_abstraction_complexity
        )
        ideology_conditioner_a = IdeologyConditionerFactory(name="A")
        ideology_conditioner_b = IdeologyConditionerFactory(name="B")

        IdeologySectionConditionerFactory(
            section=ideology_section, conditioner=ideology_conditioner_a
        )

        IdeologyConditionerConditionerFactory(
            target_conditioner=ideology_conditioner_a,
            conditioner=ideology_conditioner_b,
        )
        IdeologyConditionerConditionerFactory(
            target_conditioner=ideology_conditioner_b,
            conditioner=ideology_conditioner_a,
        )

        queryset = IdeologyConditioner.objects.get_by_complexity(
            self.ideology_abstraction_complexity.uuid
        )
        self.assertEqual(queryset.count(), 2)
