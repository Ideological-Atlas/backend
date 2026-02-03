from core.exceptions.api_exceptions import NotFoundException
from django.apps import apps
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _


class UserConditionerAnswerManager(models.Manager):
    def upsert(self, user, conditioner_uuid, validated_data):
        IdeologyConditioner = apps.get_model("ideology", "IdeologyConditioner")
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
