from core.models import TimeStampedUUIDModel
from django.db import models
from django.utils.translation import gettext_lazy as _
from ideology.models import IdeologyConditioner


class IdeologyConditionerConditioner(TimeStampedUUIDModel):
    target_conditioner = models.ForeignKey(
        IdeologyConditioner,
        on_delete=models.CASCADE,
        related_name="condition_rules",
        verbose_name=_("Target Conditioner"),
        help_text=_("The conditioner being conditioned."),
    )
    source_conditioner = models.ForeignKey(
        IdeologyConditioner,
        on_delete=models.CASCADE,
        related_name="sub_conditioner_rules",
        verbose_name=_("Source Conditioner"),
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
            "List of values that satisfy this condition (e.g. ['Spain']). Must match values in the source conditioner."
        ),
    )

    class Meta:
        verbose_name = _("Ideology Conditioner Conditioner")
        verbose_name_plural = _("Ideology Conditioner Conditioners")
        unique_together = ["target_conditioner", "source_conditioner", "name"]
        ordering = ["target_conditioner", "name"]

    def __str__(self):
        return f"{self.target_conditioner.name} -> {self.name}"
