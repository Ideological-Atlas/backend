from django.db import models
from django.utils.translation import gettext_lazy as _
from ideology.models import IdeologyConditioner

from .abstract_condition_rule import BaseConditionRule


class IdeologyConditionerConditioner(BaseConditionRule):
    target_conditioner = models.ForeignKey(
        IdeologyConditioner,
        on_delete=models.CASCADE,
        related_name="condition_rules",
        verbose_name=_("Target Conditioner"),
        help_text=_("The conditioner being conditioned."),
    )

    class Meta:
        verbose_name = _("Ideology Conditioner Conditioner")
        verbose_name_plural = _("Ideology Conditioner Conditioners")
        unique_together = ["target_conditioner", "conditioner", "name"]
        ordering = ["target_conditioner", "name"]

    def __str__(self):
        return f"{self.target_conditioner.name} -> {self.name}"
