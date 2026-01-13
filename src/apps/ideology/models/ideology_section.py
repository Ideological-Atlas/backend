from core.helpers import handle_storage
from core.models import TimeStampedUUIDModel
from django.db import models
from django.utils.translation import gettext_lazy as _
from ideology.models import IdeologyAbstractionComplexity


class IdeologySection(TimeStampedUUIDModel):
    name = models.CharField(
        max_length=128,
        verbose_name=_("Name"),
        help_text=_(
            "The title of the thematic section (e.g., 'Economics', 'Social Structure')."
        ),
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description"),
        help_text=_("A summary of the topics and concepts covered in this section."),
    )
    icon = models.ImageField(
        upload_to=handle_storage,
        blank=True,
        null=True,
        verbose_name=_("Icon"),
        help_text=_(
            "Visual representation for this section. SVG or PNG formats are recommended."
        ),
    )
    abstraction_complexity = models.ForeignKey(
        IdeologyAbstractionComplexity,
        on_delete=models.CASCADE,
        related_name="sections",
        verbose_name=_("Abstraction Complexity"),
        help_text=_("The complexity level that groups these sections."),
    )
    conditioners = models.ManyToManyField(
        "ideology.IdeologyConditioner",
        through="ideology.IdeologySectionConditioner",
        related_name="conditioned_sections",
        blank=True,
        verbose_name=_("Conditioners"),
        help_text=_("Conditioners that determine the visibility of this section."),
    )

    class Meta:
        verbose_name = _("Ideology Section")
        verbose_name_plural = _("Ideology Sections")
        ordering = ["abstraction_complexity", "name"]

    def __str__(self):
        return f"{self.name} ({self.abstraction_complexity.name})"
