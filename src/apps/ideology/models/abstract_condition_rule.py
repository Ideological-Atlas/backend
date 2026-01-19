from core.models import TimeStampedUUIDModel
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseConditionRule(TimeStampedUUIDModel):
    conditioner = models.ForeignKey(
        "ideology.IdeologyConditioner",
        on_delete=models.CASCADE,
        related_name="%(class)s_rules",
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
        abstract = True

    def clean(self):
        super().clean()
        self._validate_json_schema()
        self._validate_logical_consistency()

    def _validate_json_schema(self):
        if not isinstance(self.condition_values, list):
            raise ValidationError({"condition_values": _("Must be a list of values.")})

        if not self.condition_values:
            raise ValidationError(
                {"condition_values": _("Trigger values cannot be empty.")}
            )

    def _validate_logical_consistency(self):
        # Conditioner is now guaranteed by the abstract model
        if not self.conditioner or not self.conditioner.accepted_values:
            return

        valid_set = set(self.conditioner.accepted_values)
        current_set = set(self.condition_values)
        invalid_values = current_set - valid_set

        if invalid_values:
            raise ValidationError(
                {
                    "condition_values": _(
                        f"Values {list(invalid_values)} are not valid for conditioner '{self.conditioner.name}'."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
