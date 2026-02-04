from typing import Any, Dict, Optional, Set, Tuple

from ideology.models import (
    IdeologyAbstractionComplexity,
    IdeologyAxis,
    IdeologySection,
)


class AffinityCalculator:
    MAX_AFFINITY = 100.0
    MIN_AFFINITY = 0.0
    PARTIAL_INDIFFERENCE_SCORE = 75.0
    RANGE_SPAN = MAX_AFFINITY - MIN_AFFINITY
    MAX_POSSIBLE_GAP = 200.0

    def __init__(self, data_a: Dict[str, dict], data_b: Dict[str, dict]):
        self.data_a = data_a
        self.data_b = data_b

    def calculate_detailed(self) -> Dict[str, Any]:
        all_involved_axes = set(self.data_a.keys()) | set(self.data_b.keys())

        if not all_involved_axes:
            return {"total": None, "complexities": []}

        hierarchy_map, global_stats = self._process_axes(all_involved_axes)
        formatted_complexities = self._format_hierarchy_output(hierarchy_map)
        total_affinity = self._calculate_average(
            global_stats["score"], global_stats["count"]
        )

        return {
            "total": total_affinity,
            "complexities": formatted_complexities,
        }

    def _process_axes(
        self, axis_ids: Set[str]
    ) -> Tuple[Dict[str, Any], Dict[str, float]]:
        hierarchy_map: Dict[str, Any] = {}
        global_score = 0.0
        global_count = 0.0

        for axis_id in axis_ids:
            item_a = self.data_a.get(axis_id)
            item_b = self.data_b.get(axis_id)

            reference_item = item_a if item_a else item_b
            if not reference_item:
                continue

            complexity_uuid = reference_item["complexity_uuid"]
            section_uuid = reference_item["section_uuid"]

            self._ensure_hierarchy_structure(
                hierarchy_map, complexity_uuid, section_uuid
            )

            score = self._calculate_single_axis_score(item_a, item_b)
            rounded_score = round(score, 2) if score is not None else None

            if score is not None:
                global_score += score
                global_count += 1
                self._update_node_accumulators(
                    hierarchy_map, complexity_uuid, section_uuid, score
                )

            self._append_axis_detail(
                hierarchy_map,
                complexity_uuid,
                section_uuid,
                axis_id,
                item_a,
                item_b,
                rounded_score,
            )

        return hierarchy_map, {"score": global_score, "count": global_count}

    @staticmethod
    def _ensure_hierarchy_structure(
        hierarchy_map: Dict[str, Any], complexity_uuid: str, section_uuid: str
    ):
        if complexity_uuid not in hierarchy_map:
            hierarchy_map[complexity_uuid] = {
                "total_score": 0.0,
                "count": 0,
                "sections": {},
            }

        if section_uuid not in hierarchy_map[complexity_uuid]["sections"]:
            hierarchy_map[complexity_uuid]["sections"][section_uuid] = {
                "total_score": 0.0,
                "count": 0,
                "axes": [],
            }

    @staticmethod
    def _update_node_accumulators(
        hierarchy_map: Dict[str, Any],
        complexity_uuid: str,
        section_uuid: str,
        score: float,
    ):
        complexity_node = hierarchy_map[complexity_uuid]
        complexity_node["total_score"] += score
        complexity_node["count"] += 1

        section_node = complexity_node["sections"][section_uuid]
        section_node["total_score"] += score
        section_node["count"] += 1

    @staticmethod
    def _append_axis_detail(
        hierarchy_map: Dict[str, Any],
        complexity_uuid: str,
        section_uuid: str,
        axis_uuid: str,
        item_a: Optional[Dict],
        item_b: Optional[Dict],
        affinity: Optional[float],
    ):
        section_node = hierarchy_map[complexity_uuid]["sections"][section_uuid]
        section_node["axes"].append(
            {
                "axis_uuid": axis_uuid,
                "user_a": item_a,
                "user_b": item_b,
                "affinity": affinity,
            }
        )

    def _calculate_single_axis_score(
        self, item_a: Optional[Dict], item_b: Optional[Dict]
    ) -> Optional[float]:
        if not item_a or not item_b:
            return None

        is_indifferent_a = item_a.get("is_indifferent") or item_a.get("value") is None
        is_indifferent_b = item_b.get("is_indifferent") or item_b.get("value") is None

        if is_indifferent_a and is_indifferent_b:
            return self.MAX_AFFINITY

        if is_indifferent_a or is_indifferent_b:
            return self.PARTIAL_INDIFFERENCE_SCORE

        return self._compute_quadratic_affinity(item_a, item_b)

    def _format_hierarchy_output(
        self, hierarchy_map: Dict[str, Any]
    ) -> list[Dict[str, Any]]:
        formatted_complexities = []

        for complexity_uuid, complexity_data in hierarchy_map.items():
            formatted_sections = []

            for section_uuid, section_data in complexity_data["sections"].items():
                section_average = self._calculate_average(
                    section_data["total_score"], section_data["count"]
                )
                formatted_sections.append(
                    {
                        "section_uuid": section_uuid,
                        "affinity": section_average,
                        "axes": section_data["axes"],
                    }
                )

            complexity_average = self._calculate_average(
                complexity_data["total_score"], complexity_data["count"]
            )

            formatted_complexities.append(
                {
                    "complexity_uuid": complexity_uuid,
                    "affinity": complexity_average,
                    "sections": formatted_sections,
                }
            )

        return formatted_complexities

    @staticmethod
    def _calculate_average(total_score: float, count: float) -> Optional[float]:
        if count > 0:
            return round(total_score / count, 2)
        return None

    def _compute_quadratic_affinity(self, data_a: dict, data_b: dict) -> float:
        value_1 = float(data_a["value"])
        left_margin_1 = float(data_a["margin_left"])
        right_margin_1 = float(data_a["margin_right"])
        min_range_1, max_range_1 = value_1 - left_margin_1, value_1 + right_margin_1

        value_2 = float(data_b["value"])
        left_margin_2 = float(data_b["margin_left"])
        right_margin_2 = float(data_b["margin_right"])
        min_range_2, max_range_2 = value_2 - left_margin_2, value_2 + right_margin_2

        gap = 0.0
        if min_range_1 > max_range_2:
            gap = min_range_1 - max_range_2
        elif min_range_2 > max_range_1:
            gap = min_range_2 - max_range_1

        if gap > 0:
            ratio = min(gap / self.MAX_POSSIBLE_GAP, 1.0)
            return 50.0 * ((1.0 - ratio) ** 2)

        dist = abs(value_1 - value_2)

        if value_1 < value_2:
            max_contact_dist = right_margin_1 + left_margin_2
        else:
            max_contact_dist = right_margin_2 + left_margin_1

        if dist == 0:
            return 100.0

        ratio = min(dist / max_contact_dist, 1.0)
        return 50.0 + (50.0 * ((1.0 - ratio) ** 2))

    @staticmethod
    def hydrate_affinity_structure(affinity_data: Dict[str, Any]) -> Dict[str, Any]:
        complexity_uuids = set()
        section_uuids = set()
        axis_uuids = set()

        for complexity_item in affinity_data["complexities"]:
            complexity_uuids.add(complexity_item["complexity_uuid"])
            for section_item in complexity_item["sections"]:
                section_uuids.add(section_item["section_uuid"])
                for axis_item in section_item["axes"]:
                    axis_uuids.add(axis_item["axis_uuid"])

        complexities_map = {
            ideology_abstraction_complexity.uuid.hex: ideology_abstraction_complexity
            for ideology_abstraction_complexity in IdeologyAbstractionComplexity.objects.filter(
                uuid__in=complexity_uuids
            )
        }
        sections_map = {
            ideology_section.uuid.hex: ideology_section
            for ideology_section in IdeologySection.objects.filter(
                uuid__in=section_uuids
            )
        }
        axes_map = {
            ideology_axis.uuid.hex: ideology_axis
            for ideology_axis in IdeologyAxis.objects.filter(uuid__in=axis_uuids)
        }

        for complexity_item in affinity_data["complexities"]:
            complexity_item["complexity"] = complexities_map.get(
                complexity_item["complexity_uuid"]
            )
            for section_item in complexity_item["sections"]:
                section_item["section"] = sections_map.get(section_item["section_uuid"])
                for axis_item in section_item["axes"]:
                    axis_item["axis"] = axes_map.get(axis_item["axis_uuid"])

        return affinity_data
