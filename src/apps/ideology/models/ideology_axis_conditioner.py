from django.db import models
from django.utils.translation import gettext_lazy as _
from ideology.models import IdeologyAxis, IdeologyConditioner

from .abstract_condition_rule import BaseConditionRule


class IdeologyAxisConditioner(BaseConditionRule):
    axis = models.ForeignKey(
        IdeologyAxis,
        on_delete=models.CASCADE,
        related_name="condition_rules",
        verbose_name=_("Axis"),
        help_text=_("The axis being conditioned."),
    )
    conditioner = models.ForeignKey(
        IdeologyConditioner,
        on_delete=models.CASCADE,
        related_name="axis_rules",
        verbose_name=_("Conditioner"),
        help_text=_("The conditioner determining visibility."),
    )

    class Meta:
        verbose_name = _("Ideology Axis Conditioner")
        verbose_name_plural = _("Ideology Axis Conditioners")
        unique_together = ["axis", "conditioner", "name"]
        ordering = ["axis", "name"]

    def __str__(self):
        return f"{self.axis.name} - {self.name}"
