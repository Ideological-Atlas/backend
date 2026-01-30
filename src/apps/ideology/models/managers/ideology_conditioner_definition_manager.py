from core.exceptions.api_exceptions import NotFoundException
from django.apps import apps
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _


class IdeologyConditionerDefinitionManager(models.Manager):
    def upsert(self, ideology_uuid, conditioner_uuid, validated_data):
        Ideology = apps.get_model("ideology", "Ideology")
        IdeologyConditioner = apps.get_model("ideology", "IdeologyConditioner")

        ideology = Ideology.objects.filter(uuid=ideology_uuid).first()
        if not ideology:
            raise NotFoundException(_("Ideology not found"))

        ideology_conditioner = IdeologyConditioner.objects.filter(
            uuid=conditioner_uuid
        ).first()
        if not ideology_conditioner:
            raise NotFoundException(_("Conditioner not found"))

        defaults = {"answer": validated_data.get("answer")}

        with transaction.atomic():
            definition, created = self.update_or_create(
                ideology=ideology, conditioner=ideology_conditioner, defaults=defaults
            )
        return definition, created
