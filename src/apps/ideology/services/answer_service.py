from django.db import transaction
from django.db.models import Q
from ideology.models import (
    AxisAnswer,
    CompletedAnswer,
    ConditionerAnswer,
    IdeologyAbstractionComplexity,
    IdeologyConditioner,
)


class AnswerService:
    @staticmethod
    def generate_snapshot(user):
        with transaction.atomic():
            axis_answers = (
                AxisAnswer.objects.filter(user=user)
                .select_related(
                    "axis", "axis__section", "axis__section__abstraction_complexity"
                )
                .order_by("axis__section__name")
            )

            conditioner_answers = (
                ConditionerAnswer.objects.filter(user=user)
                .select_related("conditioner")
                .order_by("conditioner__name")
            )

            complexities = IdeologyAbstractionComplexity.objects.all().order_by(
                "complexity"
            )

            structured_data = []

            for complexity in complexities:
                complexity_data = {
                    "level": complexity.name,
                    "complexity": complexity.complexity,
                    "sections": [],
                    "conditioners": [],
                }

                complexity_axes = [
                    axis_answer
                    for axis_answer in axis_answers
                    if axis_answer.axis.section.abstraction_complexity_id
                    == complexity.id
                ]

                sections_map = {}
                for complexity_axis in complexity_axes:
                    section_name = complexity_axis.axis.section.name
                    if section_name not in sections_map:
                        sections_map[section_name] = {
                            "name": section_name,
                            "description": complexity_axis.axis.section.description,
                            "axes": [],
                        }

                    sections_map[section_name]["axes"].append(
                        {
                            "name": complexity_axis.axis.name,
                            "value": complexity_axis.value,
                            "left_label": complexity_axis.axis.left_label,
                            "right_label": complexity_axis.axis.right_label,
                        }
                    )

                complexity_data["sections"] = list(sections_map.values())

                relevant_conditioner_ids = IdeologyConditioner.objects.filter(
                    Q(section_rules__section__abstraction_complexity=complexity)
                    | Q(axis_rules__axis__section__abstraction_complexity=complexity)
                ).values_list("id", flat=True)

                complexity_conditioners = [
                    conditioner_answer
                    for conditioner_answer in conditioner_answers
                    if conditioner_answer.conditioner_id
                    in set(relevant_conditioner_ids)
                ]

                for complexity_conditioner in complexity_conditioners:
                    complexity_data["conditioners"].append(
                        {
                            "name": complexity_conditioner.conditioner.name,
                            "answer": complexity_conditioner.answer,
                            "type": complexity_conditioner.conditioner.type,
                        }
                    )

                structured_data.append(complexity_data)

            return CompletedAnswer.objects.create(
                completed_by=user, answers=structured_data
            )
