from unittest.mock import patch

from core.factories import UserFactory
from django.test import TestCase
from ideology.factories import (
    IdeologyAbstractionComplexityFactory,
    IdeologyAxisConditionerFactory,
    IdeologyAxisFactory,
    IdeologyConditionerConditionerFactory,
    IdeologyConditionerFactory,
    IdeologySectionConditionerFactory,
    IdeologySectionFactory,
    UserAxisAnswerFactory,
    UserConditionerAnswerFactory,
)
from ideology.models import CompletedAnswer, IdeologyConditioner


class CompletedAnswerManagerCoverageTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.ideology_abstraction_complexity = IdeologyAbstractionComplexityFactory(
            complexity=1, name="Comp1"
        )
        self.ideology_section = IdeologySectionFactory(
            abstraction_complexity=self.ideology_abstraction_complexity,
            name="Main Section",
        )

    def test_evaluate_axis_derived_conditioners_logic(self):
        source_ideology_axis = IdeologyAxisFactory(section=self.ideology_section)

        ideology_conditioner_range_both = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=source_ideology_axis,
            axis_min_value=40,
            axis_max_value=60,
            name="Range Both",
        )
        ideology_conditioner_range_min = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=source_ideology_axis,
            axis_min_value=40,
            axis_max_value=None,
            name="Range Min Only",
        )
        ideology_conditioner_range_max = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=source_ideology_axis,
            axis_min_value=None,
            axis_max_value=60,
            name="Range Max Only",
        )
        ideology_conditioner_fail_min = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=source_ideology_axis,
            axis_min_value=60,
            axis_max_value=None,
            name="Fail Min",
        )
        ideology_conditioner_fail_max = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=source_ideology_axis,
            axis_min_value=None,
            axis_max_value=40,
            name="Fail Max",
        )
        ideology_conditioner_no_answer = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=IdeologyAxisFactory(),
            axis_min_value=0,
            axis_max_value=100,
            name="No Answer",
        )

        conditioners_to_create = [
            ideology_conditioner_range_both,
            ideology_conditioner_range_min,
            ideology_conditioner_range_max,
            ideology_conditioner_fail_min,
            ideology_conditioner_fail_max,
            ideology_conditioner_no_answer,
        ]

        for conditioner in conditioners_to_create:
            IdeologySectionConditionerFactory(
                section=self.ideology_section, conditioner=conditioner
            )

        UserAxisAnswerFactory(user=self.user, axis=source_ideology_axis, value=50)

        snapshot = CompletedAnswer.objects.generate_snapshot(self.user)
        data = snapshot.answers

        complexity_data = next(
            item
            for item in data
            if item["complexity"] == self.ideology_abstraction_complexity.complexity
        )
        conditioners_list = complexity_data["conditioners"]
        conditioner_names = [c["name"] for c in conditioners_list]

        expected_present = ["Range Both", "Range Min Only", "Range Max Only"]
        expected_absent = ["Fail Min", "Fail Max", "No Answer"]

        for name in expected_present:
            with self.subTest(name=name, status="Present"):
                self.assertIn(name, conditioner_names)

        for name in expected_absent:
            with self.subTest(name=name, status="Absent"):
                self.assertNotIn(name, conditioner_names)

        range_both_entry = next(
            c for c in conditioners_list if c["name"] == "Range Both"
        )
        self.assertEqual(range_both_entry["answer"], "true")

    def test_enrich_tree_with_multiple_axes_same_section(self):
        ideology_axis_1 = IdeologyAxisFactory(
            section=self.ideology_section, name="Axis 1"
        )
        ideology_axis_2 = IdeologyAxisFactory(
            section=self.ideology_section, name="Axis 2"
        )

        UserAxisAnswerFactory(user=self.user, axis=ideology_axis_1, value=10)
        UserAxisAnswerFactory(user=self.user, axis=ideology_axis_2, value=20)

        snapshot = CompletedAnswer.objects.generate_snapshot(self.user)
        data = snapshot.answers

        complexity_data = data[0]
        section_data = next(
            s for s in complexity_data["sections"] if s["name"] == "Main Section"
        )

        self.assertEqual(len(section_data["axes"]), 2)
        axis_names = sorted([a["name"] for a in section_data["axes"]])
        self.assertEqual(axis_names, ["Axis 1", "Axis 2"])

    def test_build_map_with_axis_conditioners(self):
        ideology_axis = IdeologyAxisFactory(section=self.ideology_section)
        ideology_conditioner = IdeologyConditionerFactory(name="Axis Cond")

        IdeologyAxisConditionerFactory(
            axis=ideology_axis, conditioner=ideology_conditioner
        )

        UserConditionerAnswerFactory(
            user=self.user, conditioner=ideology_conditioner, answer="Yes"
        )

        snapshot = CompletedAnswer.objects.generate_snapshot(self.user)
        data = snapshot.answers

        conditioners = data[0]["conditioners"]
        names = [c["name"] for c in conditioners]
        self.assertIn("Axis Cond", names)

    def test_enrich_tree_with_axis_orphan_complexity(self):
        hidden_ideology_abstraction_complexity = IdeologyAbstractionComplexityFactory(
            complexity=99, name="Hidden"
        )
        hidden_ideology_section = IdeologySectionFactory(
            abstraction_complexity=hidden_ideology_abstraction_complexity
        )
        ideology_axis = IdeologyAxisFactory(section=hidden_ideology_section)

        UserAxisAnswerFactory(user=self.user, axis=ideology_axis, value=50)

        with patch(
            "ideology.models.IdeologyAbstractionComplexity.objects.all"
        ) as mock_all:
            mock_all.return_value.order_by.return_value = [
                self.ideology_abstraction_complexity
            ]

            snapshot = CompletedAnswer.objects.generate_snapshot(self.user)

            data = snapshot.answers
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["level"], "Comp1")
            self.assertEqual(len(data[0]["sections"]), 0)

    def test_enrich_tree_with_conditioner_orphan_complexity(self):
        hidden_ideology_abstraction_complexity = IdeologyAbstractionComplexityFactory(
            complexity=99, name="Hidden"
        )
        hidden_ideology_section = IdeologySectionFactory(
            abstraction_complexity=hidden_ideology_abstraction_complexity
        )
        ideology_conditioner = IdeologyConditionerFactory(name="Hidden Cond")

        IdeologySectionConditionerFactory(
            section=hidden_ideology_section, conditioner=ideology_conditioner
        )

        UserConditionerAnswerFactory(
            user=self.user, conditioner=ideology_conditioner, answer="Yes"
        )

        with patch(
            "ideology.models.IdeologyAbstractionComplexity.objects.all"
        ) as mock_all:
            mock_all.return_value.order_by.return_value = [
                self.ideology_abstraction_complexity
            ]

            snapshot = CompletedAnswer.objects.generate_snapshot(self.user)

            data = snapshot.answers
            conditioners = data[0]["conditioners"]
            names = [c["name"] for c in conditioners]
            self.assertNotIn("Hidden Cond", names)

    def test_recursive_complexity_mapping_deep_chain(self):
        ideology_section = IdeologySectionFactory(
            abstraction_complexity=self.ideology_abstraction_complexity
        )

        ideology_conditioner_root = IdeologyConditionerFactory(name="Cond C (Root)")
        ideology_conditioner_mid = IdeologyConditionerFactory(name="Cond B (Mid)")
        ideology_conditioner_top = IdeologyConditionerFactory(name="Cond A (Top)")

        IdeologySectionConditionerFactory(
            section=ideology_section, conditioner=ideology_conditioner_root
        )

        IdeologyConditionerConditionerFactory(
            target_conditioner=ideology_conditioner_mid,
            source_conditioner=ideology_conditioner_root,
            condition_values=["A"],
        )

        IdeologyConditionerConditionerFactory(
            target_conditioner=ideology_conditioner_top,
            source_conditioner=ideology_conditioner_mid,
            condition_values=["A"],
        )

        UserConditionerAnswerFactory(
            user=self.user, conditioner=ideology_conditioner_top, answer="Yes"
        )

        snapshot = CompletedAnswer.objects.generate_snapshot(self.user)
        data = snapshot.answers

        conditioners = data[0]["conditioners"]
        names = [c["name"] for c in conditioners]
        self.assertIn("Cond A (Top)", names)

    def test_virtual_conditioner_conflict_explicit_answer(self):
        ideology_axis = IdeologyAxisFactory()
        UserAxisAnswerFactory(user=self.user, axis=ideology_axis, value=50)

        ideology_conditioner_virtual = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=ideology_axis,
            axis_min_value=0,
            axis_max_value=100,
            name="VirtualDuplicate",
        )

        UserConditionerAnswerFactory(
            user=self.user,
            conditioner=ideology_conditioner_virtual,
            answer="ExplicitOverride",
        )

        ideology_section = IdeologySectionFactory(
            abstraction_complexity=self.ideology_abstraction_complexity
        )
        IdeologySectionConditionerFactory(
            section=ideology_section, conditioner=ideology_conditioner_virtual
        )

        snapshot = CompletedAnswer.objects.generate_snapshot(self.user)
        data = snapshot.answers

        conditioners = data[0]["conditioners"]
        target = next(c for c in conditioners if c["name"] == "VirtualDuplicate")

        self.assertEqual(target["answer"], "ExplicitOverride")

    def test_same_name_conditioner_collision(self):
        ideology_conditioner_1 = IdeologyConditionerFactory(name="SameName")
        ideology_conditioner_2 = IdeologyConditionerFactory(name="SameName")

        ideology_section = IdeologySectionFactory(
            abstraction_complexity=self.ideology_abstraction_complexity
        )

        IdeologySectionConditionerFactory(
            section=ideology_section, conditioner=ideology_conditioner_1
        )
        IdeologySectionConditionerFactory(
            section=ideology_section, conditioner=ideology_conditioner_2
        )

        UserConditionerAnswerFactory(
            user=self.user, conditioner=ideology_conditioner_1, answer="Val1"
        )
        UserConditionerAnswerFactory(
            user=self.user, conditioner=ideology_conditioner_2, answer="Val2"
        )

        snapshot = CompletedAnswer.objects.generate_snapshot(self.user)
        data = snapshot.answers

        conditioners = data[0]["conditioners"]

        matching = [c for c in conditioners if c["name"] == "SameName"]
        self.assertEqual(len(matching), 1)
