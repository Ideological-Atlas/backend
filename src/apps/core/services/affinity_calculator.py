from typing import Any, Dict, List, Optional

from ideology.services.calculation_dto import CalculationItem


class AffinityCalculator:
    MAX_AFFINITY = 100.0
    MIN_AFFINITY = 0.0
    PARTIAL_INDIFFERENCE_SCORE = 50.0
    MAX_POSSIBLE_GAP = 200.0

    COND_MATCH_BONUS = 5.0
    COND_INDIFFERENT_BONUS = 2.5
    COND_MISMATCH_PENALTY = 5.0

    MAX_COND_POSITIVE_CAP = 20.0
    MAX_COND_NEGATIVE_CAP = 25.0

    def __init__(
        self, data_a: Dict[str, CalculationItem], data_b: Dict[str, CalculationItem]
    ):
        self.data_a = data_a
        self.data_b = data_b

    def calculate_detailed(self) -> Dict[str, Any]:
        all_keys = set(self.data_a.keys()) | set(self.data_b.keys())

        hierarchy: dict = {}

        for key in all_keys:
            item = self.data_a.get(key) or self.data_b.get(key)
            if not item:
                continue

            complexity_uuid = item.complexity_uuid
            if not complexity_uuid:
                continue

            if complexity_uuid not in hierarchy:
                hierarchy[complexity_uuid] = {
                    "axes": [],
                    "conditioners": [],
                    "sections": {},
                }

            if item.type == "conditioner":
                hierarchy[complexity_uuid]["conditioners"].append(key)
            else:
                hierarchy[complexity_uuid]["axes"].append(key)
                section_uuid = item.section_uuid
                if section_uuid:
                    if section_uuid not in hierarchy[complexity_uuid]["sections"]:
                        hierarchy[complexity_uuid]["sections"][section_uuid] = []
                    hierarchy[complexity_uuid]["sections"][section_uuid].append(key)

        final_level_scores = []
        formatted_complexities = []

        for complexity_uuid, data in hierarchy.items():
            section_results = []
            complexity_axis_sum = 0.0
            complexity_axis_count = 0

            for section_uuid, axis_keys in data["sections"].items():
                sec_sum = 0.0
                sec_count = 0
                formatted_axes = []

                for axis_key in axis_keys:
                    score = self._calculate_axis_score(axis_key)
                    if score is not None:
                        sec_sum += score
                        sec_count += 1
                        complexity_axis_sum += score
                        complexity_axis_count += 1

                    user_a_dump = self.data_a.get(axis_key)
                    user_b_dump = self.data_b.get(axis_key)

                    formatted_axes.append(
                        {
                            "axis_uuid": axis_key,
                            "affinity": round(score, 2) if score is not None else None,
                            "user_a": user_a_dump.model_dump() if user_a_dump else None,
                            "user_b": user_b_dump.model_dump() if user_b_dump else None,
                        }
                    )

                sec_avg = (sec_sum / sec_count) if sec_count > 0 else None
                section_results.append(
                    {
                        "section_uuid": section_uuid,
                        "affinity": round(sec_avg, 2) if sec_avg is not None else None,
                        "axes": formatted_axes,
                    }
                )

            base_affinity = (
                (complexity_axis_sum / complexity_axis_count)
                if complexity_axis_count > 0
                else None
            )

            modifier = 0.0
            if base_affinity is not None:
                modifier = self._calculate_conditioner_modifier(data["conditioners"])

            final_score = None
            if base_affinity is not None:
                final_score = base_affinity + modifier
                final_score = max(
                    self.MIN_AFFINITY, min(self.MAX_AFFINITY, final_score)
                )
                final_level_scores.append(final_score)

            formatted_complexities.append(
                {
                    "complexity_uuid": complexity_uuid,
                    "base_affinity": (
                        round(base_affinity, 2) if base_affinity is not None else None
                    ),
                    "conditioner_modifier": round(modifier, 2),
                    "affinity": (
                        round(final_score, 2) if final_score is not None else None
                    ),
                    "sections": section_results,
                }
            )

        total_affinity = None
        if final_level_scores:
            total_affinity = sum(final_level_scores) / len(final_level_scores)
            total_affinity = round(total_affinity, 2)

        return {"total": total_affinity, "complexities": formatted_complexities}

    def _calculate_conditioner_modifier(self, conditioner_keys: List[str]) -> float:
        current_bonus = 0.0
        current_penalty = 0.0

        for key in conditioner_keys:
            item_a = self.data_a.get(key)
            item_b = self.data_b.get(key)

            if not item_a or not item_b:
                continue

            value_a = str(item_a.value or "").strip().lower()
            value_b = str(item_b.value or "").strip().lower()

            is_indifferent_a = item_a.is_indifferent
            is_indifferent_b = item_b.is_indifferent

            if value_a == value_b:
                if is_indifferent_a or is_indifferent_b:
                    current_bonus += self.COND_INDIFFERENT_BONUS
                else:
                    current_bonus += self.COND_MATCH_BONUS
            else:
                current_penalty += self.COND_MISMATCH_PENALTY

        final_bonus = min(current_bonus, self.MAX_COND_POSITIVE_CAP)
        final_penalty = min(current_penalty, self.MAX_COND_NEGATIVE_CAP)

        return final_bonus - final_penalty

    def _calculate_axis_score(self, key: str) -> Optional[float]:
        item_a = self.data_a.get(key)
        item_b = self.data_b.get(key)

        if not item_a or not item_b:
            return None

        indifferent_a = item_a.is_indifferent or item_a.value is None
        indifferent_b = item_b.is_indifferent or item_b.value is None

        if indifferent_a and indifferent_b:
            return self.MAX_AFFINITY
        if indifferent_a or indifferent_b:
            return self.PARTIAL_INDIFFERENCE_SCORE

        return self._compute_quadratic_affinity(item_a, item_b)

    def _compute_quadratic_affinity(
        self, data_a: CalculationItem, data_b: CalculationItem
    ) -> float:
        value_1, margin_left_1, margin_right_1 = (
            float(data_a.value),
            float(data_a.margin_left),
            float(data_a.margin_right),
        )
        value_2, margin_left_2, margin_right_2 = (
            float(data_b.value),
            float(data_b.margin_left),
            float(data_b.margin_right),
        )

        min_1, max_1 = value_1 - margin_left_1, value_1 + margin_right_1
        min_2, max_2 = value_2 - margin_left_2, value_2 + margin_right_2

        gap = 0.0
        if min_1 > max_2:
            gap = min_1 - max_2
        elif min_2 > max_1:
            gap = min_2 - max_1

        if gap > 0:
            ratio = min(gap / self.MAX_POSSIBLE_GAP, 1.0)
            return 50.0 * ((1.0 - ratio) ** 2)

        distance = abs(value_1 - value_2)
        contact_distance = (
            (margin_right_1 + margin_left_2)
            if value_1 < value_2
            else (margin_right_2 + margin_left_1)
        )

        if distance == 0:
            return 100.0

        ratio = min(distance / contact_distance, 1.0) if contact_distance > 0 else 1.0
        return 50.0 + (50.0 * ((1.0 - ratio) ** 2))

    @staticmethod
    def hydrate_affinity_structure(affinity_data: Dict[str, Any]) -> Dict[str, Any]:
        from ideology.models import (
            IdeologyAbstractionComplexity,
            IdeologyAxis,
            IdeologySection,
        )

        complexity_uuids = {
            complexity["complexity_uuid"]
            for complexity in affinity_data["complexities"]
        }
        section_uuids = set()
        axis_uuids = set()

        for complexity in affinity_data["complexities"]:
            for section in complexity["sections"]:
                section_uuids.add(section["section_uuid"])
                for axis in section["axes"]:
                    axis_uuids.add(axis["axis_uuid"])

        complexities = {
            o.uuid.hex: o
            for o in IdeologyAbstractionComplexity.objects.filter(
                uuid__in=complexity_uuids
            )
        }
        sections = {
            o.uuid.hex: o
            for o in IdeologySection.objects.filter(uuid__in=section_uuids)
        }
        axes = {o.uuid.hex: o for o in IdeologyAxis.objects.filter(uuid__in=axis_uuids)}

        for complexity in affinity_data["complexities"]:
            complexity["complexity"] = complexities.get(complexity["complexity_uuid"])
            for section in complexity["sections"]:
                section["section"] = sections.get(section["section_uuid"])
                for axis in section["axes"]:
                    axis["axis"] = axes.get(axis["axis_uuid"])

        return affinity_data
