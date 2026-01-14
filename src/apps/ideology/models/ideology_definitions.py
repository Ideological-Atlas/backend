from django.db import models
from django.utils.translation import gettext_lazy as _

from .abstract_answers import BaseAxisAnswer, BaseConditionerAnswer
from .ideology import Ideology


class IdeologyAxisDefinition(BaseAxisAnswer):
    ideology = models.ForeignKey(
        Ideology,
        on_delete=models.CASCADE,
        related_name="axis_definitions",
        verbose_name=_("Ideology"),
    )

    class Meta:
        verbose_name = _("Ideology Axis Definition")
        verbose_name_plural = _("Ideology Axis Definitions")
        unique_together = ["ideology", "axis"]

    def __str__(self):
        return f"{self.ideology.name} - {self.axis.name}: {self.value}"


class IdeologyConditionerDefinition(BaseConditionerAnswer):
    ideology = models.ForeignKey(
        Ideology,
        on_delete=models.CASCADE,
        related_name="conditioner_definitions",
        verbose_name=_("Ideology"),
    )

    class Meta:
        verbose_name = _("Ideology Conditioner Definition")
        verbose_name_plural = _("Ideology Conditioner Definitions")
        unique_together = ["ideology", "conditioner"]

    def __str__(self):
        return f"{self.ideology.name} - {self.conditioner.name}: {self.answer}"
