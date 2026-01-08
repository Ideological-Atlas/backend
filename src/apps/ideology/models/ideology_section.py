from core.helpers import handle_storage
from core.models import TimeStampedUUIDModel
from django.db import models
from django.utils.translation import gettext_lazy as _
from ideology.models import IdeologyAbstractionComplexity, IdeologyConditioner


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
    conditioned_by = models.ForeignKey(
        IdeologyConditioner,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dependent_sections",
        verbose_name=_("Conditioned By"),
        help_text=_(
            "Optional. Specifies a conditioner that determines the visibility or applicability of this section."
        ),
    )
    condition_values = models.JSONField(
        default=list,
        blank=True,
        null=True,
        verbose_name=_("Trigger Values"),
        help_text=_(
            "List of values that make this section visible (e.g. ['Spain']). Must match values in the conditioner."
        ),
    )

    class Meta:
        verbose_name = _("Ideology Section")
        verbose_name_plural = _("Ideology Sections")
        ordering = ["abstraction_complexity", "name"]

    def __str__(self):
        cond_str = (
            f" [If {self.conditioned_by.name} IN {self.condition_values}]"
            if self.conditioned_by
            else ""
        )
        return f"{self.name} ({self.abstraction_complexity.name}){cond_str}"
