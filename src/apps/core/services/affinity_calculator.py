from typing import Any, Dict


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
        keys_a = set(self.data_a.keys())
        keys_b = set(self.data_b.keys())
        all_involved_axes = keys_a | keys_b

        hierarchy_map: Dict[str, Dict[str, Any]] = {}
        total_global_score = 0.0
        total_global_count = 0

        if not all_involved_axes:
            return {"total": None, "complexities": []}

        for axis_id in all_involved_axes:
            item_a = self.data_a.get(axis_id)
            item_b = self.data_b.get(axis_id)

            ref_item = item_a if item_a else item_b
            if ref_item is None:
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

            if item_a and item_b:
                a_indifferent = (
                    item_a.get("is_indifferent") or item_a.get("value") is None
                )
                b_indifferent = (
                    item_b.get("is_indifferent") or item_b.get("value") is None
                )

                if a_indifferent and b_indifferent:
                    axis_score = self.MAX_AFFINITY
                elif a_indifferent or b_indifferent:
                    axis_score = self.PARTIAL_INDIFFERENCE_SCORE
                else:
                    axis_score = self._compute_quadratic_affinity(item_a, item_b)

                rounded_axis_score = round(axis_score, 2)

                total_global_score += axis_score
                total_global_count += 1

                hierarchy_map[comp_uuid]["total_score"] += axis_score
                hierarchy_map[comp_uuid]["count"] += 1

                sec_node = hierarchy_map[comp_uuid]["sections"][sec_uuid]
                sec_node["total_score"] += axis_score
                sec_node["count"] += 1

                final_axis_affinity = rounded_axis_score
            else:
                final_axis_affinity = None

            sec_node = hierarchy_map[comp_uuid]["sections"][sec_uuid]
            sec_node["axes"].append(
                {
                    "axis_uuid": axis_id,
                    "user_a": item_a,
                    "user_b": item_b,
                    "affinity": final_axis_affinity,
                }
            )

        final_complexities_list = []
        for c_uuid, c_data in hierarchy_map.items():
            sections_list = []
            for s_uuid, s_data in c_data["sections"].items():
                s_avg = None
                if s_data["count"] > 0:
                    s_avg = round(s_data["total_score"] / s_data["count"], 2)

                sections_list.append(
                    {"section_uuid": s_uuid, "affinity": s_avg, "axes": s_data["axes"]}
                )

            c_avg = None
            if c_data["count"] > 0:
                c_avg = round(c_data["total_score"] / c_data["count"], 2)

            final_complexities_list.append(
                {
                    "complexity_uuid": c_uuid,
                    "affinity": c_avg,
                    "sections": sections_list,
                }
            )

        average_global_affinity = None
        if total_global_count > 0:
            average_global_affinity = round(total_global_score / total_global_count, 2)

        return {
            "total": average_global_affinity,
            "complexities": final_complexities_list,
        }

    def _compute_quadratic_affinity(self, data_a: dict, data_b: dict) -> float:
        v1 = float(data_a["value"])
        l1 = float(data_a["margin_left"])
        r1 = float(data_a["margin_right"])
        min1, max1 = v1 - l1, v1 + r1

        v2 = float(data_b["value"])
        l2 = float(data_b["margin_left"])
        r2 = float(data_b["margin_right"])
        min2, max2 = v2 - l2, v2 + r2

        gap = 0.0
        if min1 > max2:
            gap = min1 - max2
        elif min2 > max1:
            gap = min2 - max1

        if gap > 0:
            ratio = min(gap / self.MAX_POSSIBLE_GAP, 1.0)
            return 50.0 * ((1.0 - ratio) ** 2)

        dist = abs(v1 - v2)

        if v1 < v2:
            max_contact_dist = r1 + l2
        else:
            max_contact_dist = r2 + l1

        if dist == 0:
            return 100.0

        ratio = min(dist / max_contact_dist, 1.0)
        return 50.0 + (50.0 * ((1.0 - ratio) ** 2))
