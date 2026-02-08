from typing import Dict

from core.exceptions.api_exceptions import NotFoundException
from django.apps import apps
from django.db import models, transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from ideology.services.calculation_dto import CalculationItem
from ideology.services.mapping_helpers import format_mapped_item


class UserAxisAnswerManager(models.Manager):
    def upsert(self, user, axis_uuid, validated_data):
        IdeologyAxis = apps.get_model("ideology", "IdeologyAxis")
        ideology_axis = IdeologyAxis.objects.filter(uuid=axis_uuid).first()

        if not ideology_axis:
            raise NotFoundException(_("Axis not found"))

        defaults = {
            "value": validated_data.get("value"),
            "margin_left": validated_data.get("margin_left"),
            "margin_right": validated_data.get("margin_right"),
            "is_indifferent": validated_data.get("is_indifferent", False),
        }

        with transaction.atomic():
            user_axis_answer, created = self.update_or_create(
                user=user, axis=ideology_axis, defaults=defaults
            )
        return user_axis_answer, created

    def get_mapped_for_calculation(self, user) -> Dict[str, CalculationItem]:
        queryset = (
            self.filter(user=user)
            .filter(Q(value__isnull=False) | Q(is_indifferent=True))
            .select_related(
                "axis", "axis__section", "axis__section__abstraction_complexity"
            )
        )

        return {
            answer.axis.uuid.hex: format_mapped_item(
                item_type="axis",
                value=answer.value,
                complexity_uuid=answer.axis.section.abstraction_complexity.uuid.hex,
                is_indifferent=answer.is_indifferent,
                section_uuid=answer.axis.section.uuid.hex,
                margin_left=answer.margin_left or 0,
                margin_right=answer.margin_right or 0,
            )
            for answer in queryset
        }
