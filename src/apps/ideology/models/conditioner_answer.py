from core.models import TimeStampedUUIDModel, User
from django.db import models
from django.utils.translation import gettext_lazy as _
from ideology.models import Ideology, IdeologyConditioner


class ConditionerAnswer(TimeStampedUUIDModel):
    ideology = models.ForeignKey(
        Ideology,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="conditioner_definitions",
        verbose_name=_("Ideology"),
        help_text=_(
            "The ideology defined by this answer. Leave empty if this is a user's answer."
        ),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="conditioner_answers",
        verbose_name=_("User"),
        help_text=_(
            "The user who provided this answer. Leave empty if this is defining an ideology."
        ),
    )
    conditioner = models.ForeignKey(
        IdeologyConditioner,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name=_("Conditioner"),
        help_text=_("The question or variable being answered."),
    )
    answer = models.CharField(
        max_length=255,
        verbose_name=_("Answer"),
        help_text=_(
            "The value chosen. Must match one of the 'accepted_values' defined in the conditioner."
        ),
    )

    class Meta:
        verbose_name = _("Conditioner Answer")
        verbose_name_plural = _("Conditioner Answers")
        ordering = ["conditioner", "ideology", "user"]
        constraints = [
            models.UniqueConstraint(
                fields=["ideology", "conditioner"],
                condition=models.Q(ideology__isnull=False),
                name="unique_ideology_conditioner_answer",
            ),
            models.UniqueConstraint(
                fields=["user", "conditioner"],
                condition=models.Q(user__isnull=False),
                name="unique_user_conditioner_answer",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(user__isnull=False, ideology__isnull=True)
                    | models.Q(user__isnull=True, ideology__isnull=False)
                ),
                name="conditioner_answer_owner_xor_constraint",
            ),
        ]

    def __str__(self):
        owner = self.ideology.name if self.ideology else self.user.username
        return f"{self.conditioner.name}: {self.answer} ({owner})"
