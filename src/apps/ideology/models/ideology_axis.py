from core.models import TimeStampedUUIDModel
from django.db import models
from django.utils.translation import gettext_lazy as _
from ideology.models import IdeologySection


class IdeologyAxis(TimeStampedUUIDModel):
    section = models.ForeignKey(
        IdeologySection,
        on_delete=models.CASCADE,
        related_name="axes",
        verbose_name=_("Section"),
        help_text=_("The thematic section this axis belongs to."),
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"),
        help_text=_("Internal name of the axis (e.g., 'Economic Freedom')."),
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description"),
        help_text=_("Explanation of what this axis measures."),
    )
    left_label = models.CharField(
        max_length=255,
        verbose_name=_("Left Label (0%)"),
        help_text=_(
            "Label for the start or minimum value of the axis (e.g., 'Total Control')."
        ),
    )
    right_label = models.CharField(
        max_length=255,
        verbose_name=_("Right Label (100%)"),
        help_text=_(
            "Label for the end or maximum value of the axis (e.g., 'Total Liberty')."
        ),
    )
    conditioners = models.ManyToManyField(
        "ideology.IdeologyConditioner",
        through="ideology.IdeologyAxisConditioner",
        related_name="conditioned_axes",
        blank=True,
        verbose_name=_("Conditioners"),
        help_text=_("Conditioners that determine if this axis is relevant."),
    )

    class Meta:
        verbose_name = _("Ideology Axis")
        verbose_name_plural = _("Ideology Axes")
        unique_together = ["section", "name"]
        ordering = ["section", "name"]

    def __str__(self):
        return f"{self.name} ({self.left_label} <-> {self.right_label})"
