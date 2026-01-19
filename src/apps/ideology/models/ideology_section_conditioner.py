from django.db import models
from django.utils.translation import gettext_lazy as _
from ideology.models import IdeologySection

from .abstract_condition_rule import BaseConditionRule


class IdeologySectionConditioner(BaseConditionRule):
    section = models.ForeignKey(
        IdeologySection,
        on_delete=models.CASCADE,
        related_name="condition_rules",
        verbose_name=_("Section"),
        help_text=_("The section being conditioned."),
    )

    class Meta:
        verbose_name = _("Ideology Section Conditioner")
        verbose_name_plural = _("Ideology Section Conditioners")
        unique_together = ["section", "conditioner", "name"]
        ordering = ["section", "name"]

    def __str__(self):
        return f"{self.section.name} - {self.name}"
