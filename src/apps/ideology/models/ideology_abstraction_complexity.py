from core.models import TimeStampedUUIDModel
from django.db import models
from django.utils.translation import gettext_lazy as _
from ideology.models.managers import IdeologyAbstractionComplexityManager


class IdeologyAbstractionComplexity(TimeStampedUUIDModel):
    name = models.CharField(
        max_length=128,
        unique=True,
        verbose_name=_("Name"),
        help_text=_(
            "The label for this level of abstraction (e.g., 'Concrete', 'Theoretical', 'Metaphysical')."
        ),
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Description"),
        help_text=_(
            "Detailed explanation of the characteristics that define this complexity level."
        ),
    )
    complexity = models.PositiveSmallIntegerField(
        unique=True,
        verbose_name=_("Complexity Score"),
        help_text=_(
            "A numerical value used to rank and order the levels of abstraction (e.g., 1 for lowest, 10 for highest)."
        ),
    )
    visible = models.BooleanField(
        default=True,
        verbose_name=_("Visible"),
        help_text=_(
            "Boolean to show if the level is visible or not in the frontend. Used to hide a level that is in progress or only available for certain users."
        ),
    )
    objects = IdeologyAbstractionComplexityManager()

    class Meta:
        verbose_name = _("Ideology Abstraction Complexity")
        verbose_name_plural = _("Ideology Abstraction Complexities")
        ordering = ["complexity"]

    def __str__(self):
        return f"{self.complexity} - {self.name}"
