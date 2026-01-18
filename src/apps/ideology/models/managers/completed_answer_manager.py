from typing import Any

from django.db import models


class CompletedAnswerManager(models.Manager):
    def generate_snapshot(self, user=None, data=None):
        final_data: dict[str, list[dict[str, Any]]] = {"conditioners": [], "axis": []}

        if user and user.is_authenticated:
            final_data = self._build_from_db(user)
        elif data:
            final_data = data

        return self.create(
            completed_by=user if user and user.is_authenticated else None,
            answers=final_data,
        )

    @staticmethod
    def _build_from_db(user):
        from ideology.models import UserAxisAnswer, UserConditionerAnswer

        axis_answers = UserAxisAnswer.objects.filter(user=user).select_related("axis")
        conditioner_answers = UserConditionerAnswer.objects.filter(
            user=user
        ).select_related("conditioner")

        return {
            "conditioners": [
                {
                    "uuid": answer_entry.conditioner.uuid.hex,
                    "value": answer_entry.answer,
                }
                for answer_entry in conditioner_answers
            ],
            "axis": [
                {
                    "uuid": answer_entry.axis.uuid.hex,
                    "value": answer_entry.value,
                    "margin_left": answer_entry.margin_left,
                    "margin_right": answer_entry.margin_right,
                }
                for answer_entry in axis_answers
            ],
        }
