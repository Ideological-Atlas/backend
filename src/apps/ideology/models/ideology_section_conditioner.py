from django.db import models
from django.utils.translation import gettext_lazy as _
from ideology.models import IdeologyConditioner, IdeologySection

from .abstract_condition_rule import BaseConditionRule


class IdeologySectionConditioner(BaseConditionRule):
    section = models.ForeignKey(
        IdeologySection,
        on_delete=models.CASCADE,
        related_name="condition_rules",
        verbose_name=_("Section"),
        help_text=_("The section being conditioned."),
    )
    conditioner = models.ForeignKey(
        IdeologyConditioner,
        on_delete=models.CASCADE,
        related_name="section_rules",
        verbose_name=_("Conditioner"),
        help_text=_("The conditioner determining visibility."),
    )

    class Meta:
        verbose_name = _("Ideology Section Conditioner")
        verbose_name_plural = _("Ideology Section Conditioners")
        unique_together = ["section", "conditioner", "name"]
        ordering = ["section", "name"]

    def __str__(self):
        return f"{self.section.name} - {self.name}"
