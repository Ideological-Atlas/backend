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

        ideology_conditioner_with_min_and_max_range = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=source_ideology_axis,
            axis_min_value=40,
            axis_max_value=60,
            name="Range Both",
        )
        ideology_conditioner_with_min_range_only = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=source_ideology_axis,
            axis_min_value=40,
            axis_max_value=None,
            name="Range Min Only",
        )
        ideology_conditioner_with_max_range_only = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=source_ideology_axis,
            axis_min_value=None,
            axis_max_value=60,
            name="Range Max Only",
        )
        ideology_conditioner_that_should_fail_min = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=source_ideology_axis,
            axis_min_value=60,
            axis_max_value=None,
            name="Fail Min",
        )
        ideology_conditioner_that_should_fail_max = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=source_ideology_axis,
            axis_min_value=None,
            axis_max_value=40,
            name="Fail Max",
        )
        ideology_conditioner_with_no_user_answer = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=IdeologyAxisFactory(),
            axis_min_value=0,
            axis_max_value=100,
            name="No Answer",
        )

        conditioners_to_create = [
            ideology_conditioner_with_min_and_max_range,
            ideology_conditioner_with_min_range_only,
            ideology_conditioner_with_max_range_only,
            ideology_conditioner_that_should_fail_min,
            ideology_conditioner_that_should_fail_max,
            ideology_conditioner_with_no_user_answer,
        ]

        for ideology_conditioner in conditioners_to_create:
            IdeologySectionConditionerFactory(
                section=self.ideology_section, conditioner=ideology_conditioner
            )

        UserAxisAnswerFactory(user=self.user, axis=source_ideology_axis, value=50)

        completed_answer_snapshot = CompletedAnswer.objects.generate_snapshot(self.user)
        completed_answer_data = completed_answer_snapshot.answers

        complexity_level_data = next(
            item
            for item in completed_answer_data
            if item["complexity"] == self.ideology_abstraction_complexity.complexity
        )
        generated_conditioners_list = complexity_level_data["conditioners"]
        generated_conditioner_names = [
            conditioner_data["name"] for conditioner_data in generated_conditioners_list
        ]

        expected_present_conditioner_names = [
            "Range Both",
            "Range Min Only",
            "Range Max Only",
        ]
        expected_absent_conditioner_names = ["Fail Min", "Fail Max", "No Answer"]

        for expected_name in expected_present_conditioner_names:
            with self.subTest(
                check="Conditioner should be present", conditioner_name=expected_name
            ):
                self.assertIn(expected_name, generated_conditioner_names)

        for unexpected_name in expected_absent_conditioner_names:
            with self.subTest(
                check="Conditioner should be absent", conditioner_name=unexpected_name
            ):
                self.assertNotIn(unexpected_name, generated_conditioner_names)

        target_conditioner_entry = next(
            conditioner_data
            for conditioner_data in generated_conditioners_list
            if conditioner_data["name"] == "Range Both"
        )
        self.assertEqual(target_conditioner_entry["answer"], "true")

    def test_enrich_tree_with_multiple_axes_same_section(self):
        ideology_axis_first = IdeologyAxisFactory(
            section=self.ideology_section, name="Axis 1"
        )
        ideology_axis_second = IdeologyAxisFactory(
            section=self.ideology_section, name="Axis 2"
        )

        UserAxisAnswerFactory(user=self.user, axis=ideology_axis_first, value=10)
        UserAxisAnswerFactory(user=self.user, axis=ideology_axis_second, value=20)

        completed_answer_snapshot = CompletedAnswer.objects.generate_snapshot(self.user)
        completed_answer_data = completed_answer_snapshot.answers

        first_complexity_data = completed_answer_data[0]
        target_section_data = next(
            section_data
            for section_data in first_complexity_data["sections"]
            if section_data["name"] == "Main Section"
        )

        self.assertEqual(len(target_section_data["axes"]), 2)
        axis_names_in_result = sorted(
            [axis_data["name"] for axis_data in target_section_data["axes"]]
        )
        self.assertEqual(axis_names_in_result, ["Axis 1", "Axis 2"])

    def test_build_map_with_axis_conditioners(self):
        ideology_axis = IdeologyAxisFactory(section=self.ideology_section)
        ideology_conditioner = IdeologyConditionerFactory(name="Axis Cond")

        IdeologyAxisConditionerFactory(
            axis=ideology_axis, conditioner=ideology_conditioner
        )

        UserConditionerAnswerFactory(
            user=self.user, conditioner=ideology_conditioner, answer="Yes"
        )

        completed_answer_snapshot = CompletedAnswer.objects.generate_snapshot(self.user)
        completed_answer_data = completed_answer_snapshot.answers

        conditioners_list = completed_answer_data[0]["conditioners"]
        conditioner_names = [
            conditioner_data["name"] for conditioner_data in conditioners_list
        ]
        self.assertIn("Axis Cond", conditioner_names)

    def test_enrich_tree_with_axis_orphan_complexity(self):
        hidden_ideology_abstraction_complexity = IdeologyAbstractionComplexityFactory(
            complexity=99, name="Hidden"
        )
        hidden_ideology_section = IdeologySectionFactory(
            abstraction_complexity=hidden_ideology_abstraction_complexity
        )
        ideology_axis_orphan = IdeologyAxisFactory(section=hidden_ideology_section)

        UserAxisAnswerFactory(user=self.user, axis=ideology_axis_orphan, value=50)

        with patch(
            "ideology.models.IdeologyAbstractionComplexity.objects.all"
        ) as mock_all_complexities:
            mock_all_complexities.return_value.order_by.return_value = [
                self.ideology_abstraction_complexity
            ]

            completed_answer_snapshot = CompletedAnswer.objects.generate_snapshot(
                self.user
            )

            completed_answer_data = completed_answer_snapshot.answers
            self.assertEqual(len(completed_answer_data), 1)
            self.assertEqual(completed_answer_data[0]["level"], "Comp1")
            self.assertEqual(len(completed_answer_data[0]["sections"]), 0)

    def test_enrich_tree_with_conditioner_orphan_complexity(self):
        hidden_ideology_abstraction_complexity = IdeologyAbstractionComplexityFactory(
            complexity=99, name="Hidden"
        )
        hidden_ideology_section = IdeologySectionFactory(
            abstraction_complexity=hidden_ideology_abstraction_complexity
        )
        ideology_conditioner_orphan = IdeologyConditionerFactory(name="Hidden Cond")

        IdeologySectionConditionerFactory(
            section=hidden_ideology_section, conditioner=ideology_conditioner_orphan
        )

        UserConditionerAnswerFactory(
            user=self.user, conditioner=ideology_conditioner_orphan, answer="Yes"
        )

        with patch(
            "ideology.models.IdeologyAbstractionComplexity.objects.all"
        ) as mock_all_complexities:
            mock_all_complexities.return_value.order_by.return_value = [
                self.ideology_abstraction_complexity
            ]

            completed_answer_snapshot = CompletedAnswer.objects.generate_snapshot(
                self.user
            )

            completed_answer_data = completed_answer_snapshot.answers
            conditioners_list = completed_answer_data[0]["conditioners"]
            conditioner_names = [
                conditioner_data["name"] for conditioner_data in conditioners_list
            ]
            self.assertNotIn("Hidden Cond", conditioner_names)

    def test_recursive_complexity_mapping_deep_chain(self):
        ideology_section = IdeologySectionFactory(
            abstraction_complexity=self.ideology_abstraction_complexity
        )

        ideology_conditioner_root = IdeologyConditionerFactory(name="Cond C (Root)")
        ideology_conditioner_middle = IdeologyConditionerFactory(name="Cond B (Mid)")
        ideology_conditioner_top = IdeologyConditionerFactory(name="Cond A (Top)")

        IdeologySectionConditionerFactory(
            section=ideology_section, conditioner=ideology_conditioner_root
        )

        IdeologyConditionerConditionerFactory(
            target_conditioner=ideology_conditioner_middle,
            source_conditioner=ideology_conditioner_root,
            condition_values=["Option A"],
        )

        IdeologyConditionerConditionerFactory(
            target_conditioner=ideology_conditioner_top,
            source_conditioner=ideology_conditioner_middle,
            condition_values=["Option A"],
        )

        UserConditionerAnswerFactory(
            user=self.user, conditioner=ideology_conditioner_top, answer="Yes"
        )

        completed_answer_snapshot = CompletedAnswer.objects.generate_snapshot(self.user)
        completed_answer_data = completed_answer_snapshot.answers

        conditioners_list = completed_answer_data[0]["conditioners"]
        conditioner_names = [
            conditioner_data["name"] for conditioner_data in conditioners_list
        ]
        self.assertIn("Cond A (Top)", conditioner_names)

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

        completed_answer_snapshot = CompletedAnswer.objects.generate_snapshot(self.user)
        completed_answer_data = completed_answer_snapshot.answers

        conditioners_list = completed_answer_data[0]["conditioners"]
        target_conditioner_entry = next(
            conditioner_data
            for conditioner_data in conditioners_list
            if conditioner_data["name"] == "VirtualDuplicate"
        )

        self.assertEqual(target_conditioner_entry["answer"], "ExplicitOverride")

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

        completed_answer_snapshot = CompletedAnswer.objects.generate_snapshot(self.user)
        completed_answer_data = completed_answer_snapshot.answers

        conditioners_list = completed_answer_data[0]["conditioners"]

        matching = [c for c in conditioners_list if c["name"] == "SameName"]
        self.assertEqual(len(matching), 1)
