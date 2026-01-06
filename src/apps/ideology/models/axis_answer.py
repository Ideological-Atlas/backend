from decimal import Decimal

from core.models import TimeStampedUUIDModel, User
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
    value = models.DecimalField(
        max_digits=6,
        decimal_places=4,
        validators=[
            MinValueValidator(Decimal("-1.0")),
            MaxValueValidator(Decimal("1.0")),
        ],
        verbose_name=_("Position Value"),
        help_text=_(
            "The position on the axis. Must be between -1.0 (Extreme Left) and 1.0 (Extreme Right)."
        ),
    )
    margin_left = models.DecimalField(
        max_digits=6,
        decimal_places=4,
        default=Decimal("0.0"),
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("2.0")),
        ],
        verbose_name=_("Left Margin Tolerance"),
        help_text=_(
            "Acceptable deviation towards the left side for this ideology definition."
        ),
    )
    margin_right = models.DecimalField(
        max_digits=6,
        decimal_places=4,
        default=Decimal("0.0"),
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("2.0")),
        ],
        verbose_name=_("Right Margin Tolerance"),
        help_text=_(
            "Acceptable deviation towards the right side for this ideology definition."
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
        ]

    def __str__(self):
        owner = self.ideology.name if self.ideology else self.user.username
        return f"{self.axis.name}: {self.value} ({owner})"
