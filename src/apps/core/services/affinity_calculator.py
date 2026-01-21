from typing import Any, Dict

from django.apps import apps


class AffinityCalculator:
    MAX_AFFINITY = 100.0
    MIN_AFFINITY = 0.0

    # One answers, one is missing -> 50%
    UNMATCHED_AXIS_SCORE = 50.0

    # One answers "Indifferent", the other has a value -> 75%
    # (Implies tolerance/lack of conflict, but not shared passion)
    PARTIAL_INDIFFERENCE_SCORE = 75.0

    def __init__(self, user_a, user_b):
        self.user_a = user_a
        self.user_b = user_b

    def calculate_detailed(self) -> Dict[str, Any]:
        UserAxisAnswer = apps.get_model("ideology", "UserAxisAnswer")

        answers_a = UserAxisAnswer.objects.get_mapped_for_calculation(self.user_a)
        answers_b = UserAxisAnswer.objects.get_mapped_for_calculation(self.user_b)

        keys_a = set(answers_a.keys())
        keys_b = set(answers_b.keys())
        all_involved_axes = keys_a | keys_b

        # Explicit typing fixes 'object' inference errors in mypy
        hierarchy_map: Dict[str, Dict[str, Any]] = {}
        total_global_score = 0.0

        if not all_involved_axes:
            return {"total": self.UNMATCHED_AXIS_SCORE, "complexities": []}

        for axis_id in all_involved_axes:
            item_a = answers_a.get(axis_id)
            item_b = answers_b.get(axis_id)

            ref_item = item_a if item_a else item_b
            if not ref_item:
                continue

            comp_uuid = ref_item["complexity_uuid"]
            sec_uuid = ref_item["section_uuid"]

            if comp_uuid not in hierarchy_map:
                hierarchy_map[comp_uuid] = {
                    "total_score": 0.0,
                    "count": 0,
                    "sections": {},
                }

            if sec_uuid not in hierarchy_map[comp_uuid]["sections"]:
                hierarchy_map[comp_uuid]["sections"][sec_uuid] = {
                    "total_score": 0.0,
                    "count": 0,
                    "axes": [],
                }

            # --- AFFINITY CALCULATION LOGIC ---
            axis_score = 0.0
            if item_a and item_b:
                if item_a["is_indifferent"] and item_b["is_indifferent"]:
                    # Both agree on being indifferent -> Perfect Match
                    axis_score = self.MAX_AFFINITY
                elif item_a["is_indifferent"] or item_b["is_indifferent"]:
                    # One cares, the other doesn't -> High Compatibility (Tolerance)
                    axis_score = self.PARTIAL_INDIFFERENCE_SCORE
                else:
                    # Both have specific values -> Geometric calculation
                    axis_score = self._compute_geometric_affinity(item_a, item_b)
            else:
                # One user missing data -> Neutral/Unknown
                axis_score = self.UNMATCHED_AXIS_SCORE

            rounded_axis_score = round(axis_score, 2)

            # Update Aggregates
            total_global_score += axis_score

            hierarchy_map[comp_uuid]["total_score"] += axis_score
            hierarchy_map[comp_uuid]["count"] += 1

            sec_node = hierarchy_map[comp_uuid]["sections"][sec_uuid]
            sec_node["total_score"] += axis_score
            sec_node["count"] += 1
            sec_node["axes"].append(
                {
                    "axis_uuid": axis_id,
                    "user_a": item_a,
                    "user_b": item_b,
                    "affinity": rounded_axis_score,
                }
            )

        # Build Response
        final_complexities_list = []
        for c_uuid, c_data in hierarchy_map.items():
            sections_list = []
            for s_uuid, s_data in c_data["sections"].items():
                sections_list.append(
                    {
                        "section_uuid": s_uuid,
                        "affinity": round(s_data["total_score"] / s_data["count"], 2),
                        "axes": s_data["axes"],
                    }
                )

            final_complexities_list.append(
                {
                    "complexity_uuid": c_uuid,
                    "affinity": round(c_data["total_score"] / c_data["count"], 2),
                    "sections": sections_list,
                }
            )

        average_global_affinity = (
            total_global_score / len(all_involved_axes) if all_involved_axes else 0.0
        )

        return {
            "total": round(average_global_affinity, 2),
            "complexities": final_complexities_list,
        }

    def _compute_geometric_affinity(self, data_a: dict, data_b: dict) -> float:
        v1 = float(data_a["value"])
        min1 = v1 - float(data_a["margin_left"])
        max1 = v1 + float(data_a["margin_right"])

        v2 = float(data_b["value"])
        min2 = v2 - float(data_b["margin_left"])
        max2 = v2 + float(data_b["margin_right"])

        dist = abs(v1 - v2)

        if v1 < v2:
            gap = min2 - max1
        else:
            gap = min1 - max2

        visual_gap = max(0.0, gap)

        overlap_start = max(min1, min2)
        overlap_end = min(max1, max2)
        overlap_len = max(0.0, overlap_end - overlap_start)

        union_start = min(min1, min2)
        union_end = max(max1, max2)
        union_len = max(1.0, union_end - union_start)

        iou = overlap_len / union_len

        raw_score = 100.0 - (dist * 0.5) - (visual_gap * 0.5)

        if visual_gap == 0:
            raw_score += iou * 10.0

        return max(0.0, min(100.0, raw_score))
