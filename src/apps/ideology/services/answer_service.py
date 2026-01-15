from collections import defaultdict
from typing import Any

from core.models import User
from django.db import transaction
from django.db.models import QuerySet
from ideology.models import (
    CompletedAnswer,
    IdeologyAbstractionComplexity,
    IdeologyAxisConditioner,
    IdeologyConditionerConditioner,
    IdeologySectionConditioner,
    UserAxisAnswer,
    UserConditionerAnswer,
)


class AnswerService:
    @staticmethod
    def generate_snapshot(user: User) -> CompletedAnswer:
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

            complexity_tree_structure = AnswerService._initialize_complexity_tree(
                abstraction_complexities
            )

            AnswerService._enrich_tree_with_axis_answers(
                complexity_tree_structure, user_axis_answers
            )

            conditioner_complexity_map = (
                AnswerService._build_conditioner_to_complexity_map()
            )

            AnswerService._enrich_tree_with_conditioner_answers(
                complexity_tree_structure,
                user_conditioner_answers,
                conditioner_complexity_map,
            )

            structured_final_data = AnswerService._serialize_tree_to_list(
                complexity_tree_structure, abstraction_complexities
            )

            return CompletedAnswer.objects.create(
                completed_by=user, answers=structured_final_data
            )

    @staticmethod
    def _initialize_complexity_tree(
        abstraction_complexities: QuerySet[IdeologyAbstractionComplexity],
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
        user_axis_answers: QuerySet[UserAxisAnswer],
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
            "target_conditioner_id", "source_conditioner_id"
        )

        changed = True
        while changed:
            changed = False
            for target_id, source_id in recursive_rules:
                if source_id in conditioner_to_complexity_map:
                    current_complexities = conditioner_to_complexity_map[target_id]
                    source_complexities = conditioner_to_complexity_map[source_id]

                    new_complexities = source_complexities - current_complexities
                    if new_complexities:
                        conditioner_to_complexity_map[target_id].update(
                            new_complexities
                        )
                        changed = True

        return conditioner_to_complexity_map

    @staticmethod
    def _enrich_tree_with_conditioner_answers(
        complexity_tree: dict[int, dict[str, Any]],
        user_conditioner_answers: QuerySet[UserConditionerAnswer],
        conditioner_to_complexity_map: dict[int, set[int]],
    ) -> None:
        for conditioner_answer in user_conditioner_answers:
            conditioner_id = conditioner_answer.conditioner_id
            relevant_complexity_ids = conditioner_to_complexity_map.get(
                conditioner_id, set()
            )

            conditioner_payload = {
                "name": conditioner_answer.conditioner.name,
                "answer": conditioner_answer.answer,
                "type": conditioner_answer.conditioner.type,
            }

            for complexity_id in relevant_complexity_ids:
                if complexity_id in complexity_tree:
                    complexity_tree[complexity_id]["conditioners"].append(
                        conditioner_payload
                    )

    @staticmethod
    def _serialize_tree_to_list(
        complexity_tree: dict[int, dict[str, Any]],
        abstraction_complexities: QuerySet[IdeologyAbstractionComplexity],
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
                        tree_node["conditioners"], key=lambda x: x["name"]
                    ),
                }
            )
        return serialized_data
