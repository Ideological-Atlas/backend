from typing import Dict

from core.exceptions.api_exceptions import NotFoundException
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from ideology.services.calculation_dto import CalculationItem
from ideology.services.mapping_helpers import (
    format_mapped_item,
    get_conditioner_complexity_annotation,
)


class UserConditionerAnswerManager(models.Manager):
    def upsert(self, user, conditioner_uuid, validated_data):
        from ideology.models import IdeologyConditioner

        ideology_conditioner = IdeologyConditioner.objects.filter(
            uuid=conditioner_uuid
        ).first()

        if not ideology_conditioner:
            raise NotFoundException(_("Conditioner not found"))

        defaults = {"answer": validated_data.get("answer")}

        with transaction.atomic():
            user_conditioner_answer, created = self.update_or_create(
                user=user, conditioner=ideology_conditioner, defaults=defaults
            )
        return user_conditioner_answer, created

    def get_mapped_for_calculation(self, user) -> Dict[str, CalculationItem]:
        queryset = (
            self.filter(user=user)
            .select_related("conditioner")
            .annotate(
                inferred_complexity=get_conditioner_complexity_annotation("conditioner")
            )
        )

        return {
            answer.conditioner.uuid.hex: format_mapped_item(
                item_type="conditioner",
                value=answer.answer,
                complexity_uuid=(
                    answer.inferred_complexity.hex
                    if answer.inferred_complexity
                    else None
                ),
                is_indifferent=answer.is_indifferent_answer,
            )
            for answer in queryset
        }
