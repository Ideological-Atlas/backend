import hashlib
import json
from typing import Any

from django.db import models


class CompletedAnswerManager(models.Manager):
    def generate_snapshot(self, user=None, input_data=None):
        final_data: dict[str, list[dict[str, Any]]] = {
            "conditioners": [],
            "axis": [],
        }
        user_object = user if user and user.is_authenticated else None

        if user_object:
            final_data = self._build_from_db(user_object)
        elif input_data:
            processed_input = self._process_anonymous_input_data(input_data)
            final_data = self._normalize_data(processed_input)

        data_hash = self._calculate_hash(final_data)

        existing_answer = self.filter(
            completed_by=user_object, answer_hash=data_hash
        ).first()

        if existing_answer:
            return existing_answer

        return self.create(
            completed_by=user_object,
            answers=final_data,
            answer_hash=data_hash,
        )

    @staticmethod
    def _process_anonymous_input_data(input_data: dict[str, Any]) -> dict[str, Any]:
        axis_data = [
            {**item, "uuid": item["uuid"].hex} for item in input_data.get("axis", [])
        ]
        conditioners_data = [
            {**item, "uuid": item["uuid"].hex}
            for item in input_data.get("conditioners", [])
        ]
        return {
            "axis": axis_data,
            "conditioners": conditioners_data,
        }

    @staticmethod
    def _calculate_hash(data: dict) -> str:
        json_string = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_string.encode("utf-8")).hexdigest()

    @staticmethod
    def _build_from_db(user):
        from ideology.models import UserAxisAnswer, UserConditionerAnswer

        user_axis_answers = (
            UserAxisAnswer.objects.filter(user=user)
            .select_related("axis")
            .order_by("axis__uuid")
        )
        user_conditioner_answers = (
            UserConditionerAnswer.objects.filter(user=user)
            .select_related("conditioner")
            .order_by("conditioner__uuid")
        )

        return {
            "conditioners": [
                {
                    "uuid": user_conditioner_answer.conditioner.uuid.hex,
                    "value": user_conditioner_answer.answer,
                }
                for user_conditioner_answer in user_conditioner_answers
            ],
            "axis": [
                {
                    "uuid": user_axis_answer.axis.uuid.hex,
                    "value": user_axis_answer.value,
                    "margin_left": user_axis_answer.margin_left,
                    "margin_right": user_axis_answer.margin_right,
                }
                for user_axis_answer in user_axis_answers
            ],
        }

    @staticmethod
    def _normalize_data(data: dict) -> dict:
        normalized_data = {
            "conditioners": sorted(
                data.get("conditioners", []), key=lambda item: item.get("uuid", "")
            ),
            "axis": sorted(data.get("axis", []), key=lambda item: item.get("uuid", "")),
        }
        return normalized_data
