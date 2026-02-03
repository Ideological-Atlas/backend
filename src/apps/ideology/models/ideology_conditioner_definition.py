from django.db import models
from django.utils.translation import gettext_lazy as _
from ideology.models.managers import IdeologyConditionerDefinitionManager

from .abstract_answers import BaseConditionerAnswer
from .ideology import Ideology


class IdeologyConditionerDefinition(BaseConditionerAnswer):
    ideology = models.ForeignKey(
        Ideology,
        on_delete=models.CASCADE,
        related_name="conditioner_definitions",
        verbose_name=_("Ideology"),
    )

    objects = IdeologyConditionerDefinitionManager()

    class Meta:
        verbose_name = _("Ideology Conditioner Definition")
        verbose_name_plural = _("Ideology Conditioner Definitions")
        unique_together = ["ideology", "conditioner"]

    def __str__(self):
        return f"{self.ideology.name} - {self.conditioner.name}: {self.answer}"
