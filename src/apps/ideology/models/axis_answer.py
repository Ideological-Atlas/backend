from core.models import TimeStampedUUIDModel, User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from ideology.models import Ideology, IdeologyAxis


class AxisAnswer(TimeStampedUUIDModel):
    ideology = models.ForeignKey(
        Ideology,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="axis_definitions",
        verbose_name=_("Ideology"),
        help_text=_(
            "The ideology defined by this position. Leave empty if this is a user's result."
        ),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="axis_results",
        verbose_name=_("User"),
        help_text=_(
            "The user who obtained this result. Leave empty if this is defining an ideology."
        ),
    )
    axis = models.ForeignKey(
        IdeologyAxis,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name=_("Axis"),
        help_text=_("The specific axis being measured."),
    )
    is_indifferent = models.BooleanField(
        default=False,
        verbose_name=_("Is Indifferent"),
        help_text=_("If true, the user is indifferent to this axis (no value)."),
    )
    value = models.IntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(-100),
            MaxValueValidator(100),
        ],
        verbose_name=_("Position Value"),
        help_text=_(
            "The position on the axis. Must be between -100 (Extreme Left) and 100 (Extreme Right)."
        ),
    )
    margin_left = models.IntegerField(
        default=0,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(200),
        ],
        verbose_name=_("Left Margin Tolerance"),
        help_text=_(
            "Positive magnitude of deviation allowed towards the left. (Value - Margin Left >= -100)"
        ),
    )
    margin_right = models.IntegerField(
        default=0,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(200),
        ],
        verbose_name=_("Right Margin Tolerance"),
        help_text=_(
            "Positive magnitude of deviation allowed towards the right. (Value + Margin Right <= 100)"
        ),
    )

    class Meta:
        verbose_name = _("Axis Answer")
        verbose_name_plural = _("Axis Answers")
        ordering = ["axis", "ideology", "user"]
        constraints = [
            models.UniqueConstraint(
                fields=["ideology", "axis"],
                condition=models.Q(ideology__isnull=False),
                name="unique_ideology_axis_position",
            ),
            models.UniqueConstraint(
                fields=["user", "axis"],
                condition=models.Q(user__isnull=False),
                name="unique_user_axis_result",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(user__isnull=False, ideology__isnull=True)
                    | models.Q(user__isnull=True, ideology__isnull=False)
                ),
                name="axis_answer_owner_xor_constraint",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(value__isnull=True)
                    | models.Q(value__gte=models.F("margin_left") - 100)
                ),
                name="axis_answer_lower_bound_check",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(value__isnull=True)
                    | models.Q(value__lte=100 - models.F("margin_right"))
                ),
                name="axis_answer_upper_bound_check",
            ),
        ]

    def _validate_margins(self):
        if (self.value - self.margin_left) < -100:
            raise ValidationError(
                _(
                    f"Lower bound error: Position ({self.value}) minus Left Margin ({self.margin_left}) is less than -100"
                )
            )

        if (self.value + self.margin_right) > 100:
            raise ValidationError(
                _(
                    f"Upper bound error: Position ({self.value}) plus Right Margin ({self.margin_right}) is greater than 100"
                )
            )

    def _validate_indifference(self):
        if self.is_indifferent:
            self.value = None
            self.margin_left = None
            self.margin_right = None
        else:
            if not self.value:
                raise ValidationError(
                    _("A non-indifferent answer must have a numeric value.")
                )
            self._validate_margins()

    def clean(self):
        super().clean()
        self._validate_indifference()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        owner = self.ideology.name if self.ideology else self.user.username
        val_str = "Indifferent" if self.is_indifferent else str(self.value)
        return f"{self.axis.name}: {val_str} ({owner})"
