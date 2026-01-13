from core.models import TimeStampedUUIDModel
from django.db import models
from django.utils.translation import gettext_lazy as _
from ideology.models import IdeologyConditioner, IdeologySection


class IdeologySectionConditioner(TimeStampedUUIDModel):
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
    name = models.CharField(
        max_length=128,
        verbose_name=_("Name"),
        help_text=_("Name of this condition rule."),
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description"),
        help_text=_("Description of the logic applied in this rule."),
    )
    condition_values = models.JSONField(
        default=list,
        blank=True,
        null=True,
        verbose_name=_("Trigger Values"),
        help_text=_(
            "List of values that satisfy this condition (e.g. ['Spain']). Must match values in the conditioner."
        ),
    )

    class Meta:
        verbose_name = _("Ideology Section Conditioner")
        verbose_name_plural = _("Ideology Section Conditioners")
        unique_together = ["section", "conditioner", "name"]
        ordering = ["section", "name"]

    def __str__(self):
        return f"{self.section.name} - {self.name}"
