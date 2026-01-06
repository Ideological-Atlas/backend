from core.models import TimeStampedUUIDModel
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _
from ideology.models import IdeologyAbstractionComplexity


class IdeologyConditioner(TimeStampedUUIDModel):
    class ConditionerType(models.TextChoices):
        BOOLEAN = "boolean", _("Boolean (Yes/No)")
        CATEGORICAL = "categorical", _("Categorical (Selection)")
        SCALE = "scale", _("Scale (Numeric Range)")
        NUMERIC = "numeric", _("Numeric Value")
        TEXT = "text", _("Free Text")

    name = models.CharField(
        max_length=128,
        verbose_name=_("Name"),
        help_text=_("The name of the conditioner or variable."),
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description"),
        help_text=_(
            "Detailed explanation of what this conditioner measures or defines within an ideology."
        ),
    )
    type = models.CharField(
        max_length=20,
        choices=ConditionerType.choices,
        default=ConditionerType.CATEGORICAL,
        verbose_name=_("Type"),
        help_text=_("Defines the format of the data expected for this conditioner."),
    )
    abstraction_complexity = models.ForeignKey(
        IdeologyAbstractionComplexity,
        on_delete=models.CASCADE,
        related_name="conditioners",
        verbose_name=_("Abstraction Complexity"),
        help_text=_("The complexity level that groups these conditioners."),
    )
    accepted_values = ArrayField(
        models.CharField(max_length=128),
        blank=True,
        null=True,
        verbose_name=_("Accepted Values"),
        help_text=_(
            "List of valid options if the type is 'Categorical' (comma-separated in admin). Leave empty for other types."
        ),
    )

    class Meta:
        verbose_name = _("Ideology Conditioner")
        verbose_name_plural = _("Ideology Conditioners")
        ordering = ["abstraction_complexity", "name"]

    def __str__(self):
        return self.name
