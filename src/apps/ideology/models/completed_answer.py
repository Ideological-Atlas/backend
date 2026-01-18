from core.models import TimeStampedUUIDModel, User
from django.db import models
from django.utils.translation import gettext_lazy as _
from ideology.models.managers import CompletedAnswerManager


class CompletedAnswer(TimeStampedUUIDModel):
    completed_by = models.ForeignKey(
        User,
        null=True,
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
    answer_hash = models.CharField(
        max_length=64,
        db_index=True,
        blank=True,
        editable=False,
        verbose_name=_("Answer Hash"),
        help_text=_("SHA-256 hash of the normalized answers for fast deduplication."),
    )

    objects = CompletedAnswerManager()

    class Meta:
        verbose_name = _("Completed Answer")
        verbose_name_plural = _("Completed Answers")
        ordering = ["-created"]

    def __str__(self):
        username = self.completed_by.username if self.completed_by else _("Anonymous")
        return f"Answers by {username} ({self.created.strftime('%Y-%m-%d')})"
