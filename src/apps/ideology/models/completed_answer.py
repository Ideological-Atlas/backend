import uuid

from core.models import TimeStampedUUIDModel, User
from django.apps import apps
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

    def get_mapped_for_calculation(self) -> dict[str, dict]:
        IdeologyAxis = apps.get_model("ideology", "IdeologyAxis")

        raw_axes = self.answers.get("axis", [])
        if not raw_axes:
            return {}

        axis_uuids = []
        for item in raw_axes:
            try:
                axis_uuids.append(uuid.UUID(item["uuid"]))
            except (ValueError, TypeError, AttributeError):
                continue

        hierarchy_map = {
            ax["uuid"].hex: {
                "section_uuid": ax["section__uuid"].hex,
                "complexity_uuid": ax["section__abstraction_complexity__uuid"].hex,
            }
            for ax in IdeologyAxis.objects.filter(uuid__in=axis_uuids).values(
                "uuid", "section__uuid", "section__abstraction_complexity__uuid"
            )
        }

        mapped_data = {}
        for item in raw_axes:
            try:
                raw_uuid = item.get("uuid")
                if not isinstance(raw_uuid, str):
                    continue
                clean_uuid = raw_uuid.replace("-", "")
            except (AttributeError, ValueError):
                continue

            if clean_uuid not in hierarchy_map:
                continue

            mapped_data[clean_uuid] = {
                "value": item.get("value"),
                "margin_left": item.get("margin_left", 0),
                "margin_right": item.get("margin_right", 0),
                "is_indifferent": item.get("is_indifferent", False),
                "section_uuid": hierarchy_map[clean_uuid]["section_uuid"],
                "complexity_uuid": hierarchy_map[clean_uuid]["complexity_uuid"],
            }

        return mapped_data
