from collections import defaultdict
from typing import Any

from django.db import models, transaction
from django.db.models import QuerySet


class CompletedAnswerManager(models.Manager):
    def generate_snapshot(self, user):
        from ideology.models import (
            IdeologyAbstractionComplexity,
            UserAxisAnswer,
            UserConditionerAnswer,
        )

        with transaction.atomic():
            abstraction_complexities = (
                IdeologyAbstractionComplexity.objects.all().order_by("complexity")
            )

            user_axis_answers = UserAxisAnswer.objects.filter(user=user).select_related(
                "axis",
                "axis__section",
                "axis__section__abstraction_complexity",
            )

            user_conditioner_answers = UserConditionerAnswer.objects.filter(
                user=user
            ).select_related("conditioner")

            complexity_tree_structure = self._initialize_complexity_tree(
                abstraction_complexities
            )

            self._enrich_tree_with_axis_answers(
                complexity_tree_structure, user_axis_answers
            )

            virtual_conditioner_ids = self._evaluate_axis_derived_conditioners(
                user_axis_answers
            )

            conditioner_complexity_map = self._build_conditioner_to_complexity_map()

            self._enrich_tree_with_conditioner_answers(
                complexity_tree_structure,
                user_conditioner_answers,
                conditioner_complexity_map,
                virtual_conditioner_ids,
            )

            structured_final_data = self._serialize_tree_to_list(
                complexity_tree_structure, abstraction_complexities
            )

            return self.create(completed_by=user, answers=structured_final_data)

    @staticmethod
    def _evaluate_axis_derived_conditioners(
        user_axis_answers: QuerySet,
    ) -> set[int]:
        from ideology.models import IdeologyConditioner

        active_virtual_conditioner_ids: set[int] = set()

        answers_map = {
            user_axis_answer.axis_id: user_axis_answer
            for user_axis_answer in user_axis_answers
            if user_axis_answer.value is not None
        }

        if not answers_map:
            return active_virtual_conditioner_ids

        axis_derived_conditioners = IdeologyConditioner.objects.filter(
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE
        ).select_related("source_axis")

        for ideology_conditioner in axis_derived_conditioners:
            if (
                not ideology_conditioner.source_axis_id
                or ideology_conditioner.source_axis_id not in answers_map
            ):
                continue

            user_value = answers_map[ideology_conditioner.source_axis_id].value

            meets_min = True
            if ideology_conditioner.axis_min_value is not None:
                meets_min = user_value >= ideology_conditioner.axis_min_value

            meets_max = True
            if ideology_conditioner.axis_max_value is not None:
                meets_max = user_value <= ideology_conditioner.axis_max_value

            if meets_min and meets_max:
                active_virtual_conditioner_ids.add(ideology_conditioner.id)

        return active_virtual_conditioner_ids

    @staticmethod
    def _initialize_complexity_tree(
        abstraction_complexities: QuerySet,
    ) -> dict[int, dict[str, Any]]:
        return {
            abstraction_complexity.id: {
                "meta": abstraction_complexity,
                "sections": {},
                "conditioners": [],
            }
            for abstraction_complexity in abstraction_complexities
        }

    @staticmethod
    def _enrich_tree_with_axis_answers(
        complexity_tree: dict[int, dict[str, Any]],
        user_axis_answers: QuerySet,
    ) -> None:
        for axis_answer in user_axis_answers:
            complexity_id = axis_answer.axis.section.abstraction_complexity_id

            if complexity_id not in complexity_tree:
                continue

            section_name = axis_answer.axis.section.name
            complexity_node = complexity_tree[complexity_id]
            sections_group = complexity_node["sections"]

            if section_name not in sections_group:
                sections_group[section_name] = {
                    "name": section_name,
                    "description": axis_answer.axis.section.description,
                    "axes": [],
                }

            sections_group[section_name]["axes"].append(
                {
                    "name": axis_answer.axis.name,
                    "value": axis_answer.value,
                    "left_label": axis_answer.axis.left_label,
                    "right_label": axis_answer.axis.right_label,
                }
            )

    @staticmethod
    def _build_conditioner_to_complexity_map() -> dict[int, set[int]]:
        from ideology.models import (
            IdeologyAxisConditioner,
            IdeologyConditionerConditioner,
            IdeologySectionConditioner,
        )

        conditioner_to_complexity_map: dict[int, set[int]] = defaultdict(set)

        section_rules = IdeologySectionConditioner.objects.values_list(
            "conditioner_id", "section__abstraction_complexity_id"
        )
        for conditioner_id, complexity_id in section_rules:
            conditioner_to_complexity_map[conditioner_id].add(complexity_id)

        axis_rules = IdeologyAxisConditioner.objects.values_list(
            "conditioner_id", "axis__section__abstraction_complexity_id"
        )
        for conditioner_id, complexity_id in axis_rules:
            conditioner_to_complexity_map[conditioner_id].add(complexity_id)

        recursive_rules = IdeologyConditionerConditioner.objects.values_list(
            "target_conditioner_id", "conditioner_id"
        )

        has_changes = True
        while has_changes:
            has_changes = False
            for target_id, source_id in recursive_rules:
                if source_id in conditioner_to_complexity_map:
                    current_complexities = conditioner_to_complexity_map[target_id]
                    source_complexities = conditioner_to_complexity_map[source_id]

                    new_complexities = source_complexities - current_complexities
                    if new_complexities:
                        conditioner_to_complexity_map[target_id].update(
                            new_complexities
                        )
                        has_changes = True

        return conditioner_to_complexity_map

    def _enrich_tree_with_conditioner_answers(
        self,
        complexity_tree: dict[int, dict[str, Any]],
        user_conditioner_answers: QuerySet,
        conditioner_to_complexity_map: dict[int, set[int]],
        virtual_conditioner_ids: set[int],
    ) -> None:
        from ideology.models import IdeologyConditioner

        processed_conditioner_ids = set()

        for conditioner_answer in user_conditioner_answers:
            conditioner_id = conditioner_answer.conditioner_id
            processed_conditioner_ids.add(conditioner_id)

            self._add_to_tree(
                complexity_tree,
                conditioner_to_complexity_map,
                conditioner_answer.conditioner,
                conditioner_answer.answer,
            )

        if virtual_conditioner_ids:
            virtual_conditioner_objects = IdeologyConditioner.objects.filter(
                id__in=virtual_conditioner_ids
            )
            for ideology_conditioner in virtual_conditioner_objects:
                if ideology_conditioner.id not in processed_conditioner_ids:
                    self._add_to_tree(
                        complexity_tree,
                        conditioner_to_complexity_map,
                        ideology_conditioner,
                        "true",
                    )

    @staticmethod
    def _add_to_tree(
        complexity_tree: dict[int, dict[str, Any]],
        conditioner_to_complexity_map: dict[int, set[int]],
        ideology_conditioner,
        answer_value: str,
    ) -> None:
        relevant_complexity_ids = conditioner_to_complexity_map.get(
            ideology_conditioner.id, set()
        )

        payload = {
            "name": ideology_conditioner.name,
            "answer": answer_value,
            "type": ideology_conditioner.type,
        }

        for complexity_id in relevant_complexity_ids:
            if complexity_id in complexity_tree:
                existing_entries = [
                    conditioner_entry
                    for conditioner_entry in complexity_tree[complexity_id][
                        "conditioners"
                    ]
                    if conditioner_entry["name"] == ideology_conditioner.name
                ]
                if not existing_entries:
                    complexity_tree[complexity_id]["conditioners"].append(payload)

    @staticmethod
    def _serialize_tree_to_list(
        complexity_tree: dict[int, dict[str, Any]],
        abstraction_complexities: QuerySet,
    ) -> list[dict[str, Any]]:
        serialized_data = []
        for abstraction_complexity in abstraction_complexities:
            tree_node = complexity_tree[abstraction_complexity.id]
            serialized_data.append(
                {
                    "level": abstraction_complexity.name,
                    "complexity": abstraction_complexity.complexity,
                    "sections": list(tree_node["sections"].values()),
                    "conditioners": sorted(
                        tree_node["conditioners"],
                        key=lambda conditioner_item: conditioner_item["name"],
                    ),
                }
            )
        return serialized_data
