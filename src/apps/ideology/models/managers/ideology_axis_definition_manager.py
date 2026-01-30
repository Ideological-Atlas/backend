from core.exceptions.api_exceptions import NotFoundException
from django.apps import apps
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _


class IdeologyAxisDefinitionManager(models.Manager):
    def upsert(self, ideology_uuid, axis_uuid, validated_data):
        Ideology = apps.get_model("ideology", "Ideology")
        IdeologyAxis = apps.get_model("ideology", "IdeologyAxis")

        ideology = Ideology.objects.filter(uuid=ideology_uuid).first()
        if not ideology:
            raise NotFoundException(_("Ideology not found"))

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
            definition, created = self.update_or_create(
                ideology=ideology, axis=ideology_axis, defaults=defaults
            )
        return definition, created
