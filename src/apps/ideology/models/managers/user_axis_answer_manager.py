from core.exceptions.api_exceptions import NotFoundException
from django.apps import apps
from django.db import models, transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


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

    def get_mapped_for_calculation(self, user) -> dict[str, dict]:
        queryset = (
            self.filter(user=user)
            .filter(Q(value__isnull=False) | Q(is_indifferent=True))
            .values(
                "axis__uuid",
                "value",
                "margin_left",
                "margin_right",
                "is_indifferent",
                "axis__section__uuid",
                "axis__section__abstraction_complexity__uuid",
            )
        )

        return {
            item["axis__uuid"].hex: {
                "value": item["value"],
                "margin_left": item["margin_left"] or 0,
                "margin_right": item["margin_right"] or 0,
                "is_indifferent": item["is_indifferent"],
                "section_uuid": item["axis__section__uuid"].hex,
                "complexity_uuid": item[
                    "axis__section__abstraction_complexity__uuid"
                ].hex,
            }
            for item in queryset
        }
