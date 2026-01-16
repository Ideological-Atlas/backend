from core.models import TimeStampedUUIDModel, User
from django.db import models
from django.utils.translation import gettext_lazy as _
from ideology.models.managers import CompletedAnswerManager


class CompletedAnswer(TimeStampedUUIDModel):
    completed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="completed_answers",
        verbose_name=_("Completed By"),
        help_text=_("The user who submitted this set of answers."),
    )
    answers = models.JSONField(
        default=dict,
        verbose_name=_("Answers Data"),
        help_text=_(
            "Structured JSON containing the full set of answers provided by the user."
        ),
    )

    objects = CompletedAnswerManager()

    class Meta:
        verbose_name = _("Completed Answer")
        verbose_name_plural = _("Completed Answers")
        ordering = ["-created"]

    def __str__(self):
        return f"Answers by {self.completed_by.username} ({self.created.strftime('%Y-%m-%d')})"
