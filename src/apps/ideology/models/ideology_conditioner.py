from core.models import TimeStampedUUIDModel
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


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
    accepted_values = models.JSONField(
        default=list,
        blank=True,
        null=True,
        verbose_name=_("Accepted Values"),
        help_text=_(
            "List of valid options if the type is 'Categorical'. Format: ['Option A', 'Option B']."
        ),
    )
    conditioners = models.ManyToManyField(
        "self",
        through="ideology.IdeologyConditionerConditioner",
        symmetrical=False,
        related_name="conditioned_by",
        blank=True,
        verbose_name=_("Conditioners"),
        help_text=_("Conditioners that determine the visibility of this conditioner."),
    )

    class Meta:
        verbose_name = _("Ideology Conditioner")
        verbose_name_plural = _("Ideology Conditioners")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.type == self.ConditionerType.BOOLEAN:
            expected = ["true", "false"]
            if not self.accepted_values or sorted(self.accepted_values) != sorted(
                expected
            ):
                raise ValidationError(
                    {
                        "accepted_values": _(
                            "Boolean type must have accepted_values=['true', 'false']"
                        )
                    }
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
