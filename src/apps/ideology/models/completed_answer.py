import uuid
from typing import Any, Dict, List

from core.models import TimeStampedUUIDModel, User
from django.db import models
from django.utils.translation import gettext_lazy as _
from ideology.models import (
    IdeologyAxis,
    IdeologyConditioner,
    IdeologyConditionerDefinition,
)
from ideology.models.managers import CompletedAnswerManager
from ideology.services.calculation_dto import CalculationItem
from ideology.services.mapping_helpers import (
    format_mapped_item,
    get_conditioner_complexity_annotation,
)


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

    def get_mapped_for_calculation(self) -> Dict[str, CalculationItem]:
        return {**self._map_axes(), **self._map_conditioners()}

    def _map_axes(self) -> Dict[str, CalculationItem]:
        raw_axes = self.answers.get("axis", [])
        if not raw_axes:
            return {}

        hierarchy_map = self._build_axis_hierarchy_map(raw_axes)
        mapped_axes = {}

        for axis in raw_axes:
            clean_uuid = self._extract_uuid(axis)
            if not clean_uuid or clean_uuid not in hierarchy_map:
                continue

            mapped_axes[clean_uuid] = format_mapped_item(
                item_type="axis",
                value=axis.get("value"),
                complexity_uuid=hierarchy_map[clean_uuid]["complexity_uuid"],
                is_indifferent=axis.get("is_indifferent", False),
                section_uuid=hierarchy_map[clean_uuid]["section_uuid"],
                margin_left=axis.get("margin_left", 0),
                margin_right=axis.get("margin_right", 0),
            )
        return mapped_axes

    def _map_conditioners(self) -> Dict[str, CalculationItem]:
        raw_conditioners = self.answers.get("conditioners", [])
        if not raw_conditioners:
            return {}

        complexity_map = self._build_conditioner_complexity_map(raw_conditioners)
        mapped_conditioners = {}

        for item in raw_conditioners:
            clean_uuid = self._extract_uuid(item)
            if not clean_uuid:
                continue

            value = str(item.get("value", "")).strip()

            mapped_conditioners[clean_uuid] = format_mapped_item(
                item_type="conditioner",
                value=value,
                complexity_uuid=complexity_map.get(clean_uuid),
                is_indifferent=value.lower()
                in IdeologyConditionerDefinition.INDIFFERENT_TERMS,
            )
        return mapped_conditioners

    @staticmethod
    def _build_axis_hierarchy_map(raw_axes: List[Dict]) -> Dict[str, Dict[str, str]]:
        axis_uuids = []
        for item in raw_axes:
            try:
                axis_uuids.append(uuid.UUID(item["uuid"]))
            except (ValueError, TypeError, KeyError, AttributeError):
                continue

        if not axis_uuids:
            return {}

        ideology_axis_queryset = IdeologyAxis.objects.filter(
            uuid__in=axis_uuids
        ).values("uuid", "section__uuid", "section__abstraction_complexity__uuid")

        return {
            axis["uuid"].hex: {
                "section_uuid": axis["section__uuid"].hex,
                "complexity_uuid": axis["section__abstraction_complexity__uuid"].hex,
            }
            for axis in ideology_axis_queryset
        }

    @staticmethod
    def _build_conditioner_complexity_map(
        raw_conditioners: List[Dict],
    ) -> Dict[str, str]:
        cond_uuids = []
        for item in raw_conditioners:
            try:
                cond_uuids.append(uuid.UUID(item["uuid"]))
            except (ValueError, TypeError, KeyError, AttributeError):
                continue

        if not cond_uuids:
            return {}

        ideology_conditioner_queryset = (
            IdeologyConditioner.objects.filter(uuid__in=cond_uuids)
            .annotate(
                inferred_complexity=get_conditioner_complexity_annotation(prefix="")
            )
            .values("uuid", "inferred_complexity")
        )

        return {
            conditioner["uuid"].hex: conditioner["inferred_complexity"].hex
            for conditioner in ideology_conditioner_queryset
            if conditioner["inferred_complexity"]
        }

    @staticmethod
    def _extract_uuid(item: Dict[str, Any]) -> str | None:
        try:
            raw_uuid = item.get("uuid")
            if isinstance(raw_uuid, str):
                return uuid.UUID(raw_uuid).hex
        except (AttributeError, ValueError, TypeError):
            pass
        return None
