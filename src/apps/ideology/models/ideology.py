from typing import Dict

from core.helpers import handle_storage
from core.models import TimeStampedUUIDModel, VisibleMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from ideology.models.managers import IdeologyManager
from ideology.services.calculation_dto import CalculationItem
from ideology.services.mapping_helpers import (
    format_mapped_item,
    get_conditioner_complexity_annotation,
)


class Ideology(VisibleMixin, TimeStampedUUIDModel):
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("Name"),
        help_text=_("Ideology Name"),
        db_index=True,
    )
    description_supporter = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Supporter description"),
        help_text=_("Ideology Description from the point of view of a supporter"),
    )
    description_detractor = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Detractor description"),
        help_text=_("Ideology Description the point of view of a detractor"),
    )
    description_neutral = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Neutral description"),
        help_text=_("Ideology Description the point of view of a neutral"),
    )
    flag = models.ImageField(
        blank=True,
        null=True,
        upload_to=handle_storage,
        verbose_name=_("Flag"),
        help_text=_("Ideology Flag Image"),
    )
    background = models.ImageField(
        blank=True,
        null=True,
        upload_to=handle_storage,
        verbose_name=_("Background"),
        help_text=_("Ideology Background Image"),
    )
    color = models.CharField(
        max_length=16,
        blank=True,
        null=True,
        verbose_name=_("Color"),
        help_text=_("Ideology Color Image"),
    )
    associated_countries = models.ManyToManyField(
        "core.Country",
        through="ideology.IdeologyAssociation",
        related_name="ideologies",
        blank=True,
        verbose_name=_("Associated Countries"),
        help_text=_("Countries where this ideology is explicitly present."),
    )
    associated_regions = models.ManyToManyField(
        "core.Region",
        through="ideology.IdeologyAssociation",
        related_name="ideologies",
        blank=True,
        verbose_name=_("Associated Regions"),
        help_text=_("Specific regions where this ideology is explicitly present."),
    )
    associated_religions = models.ManyToManyField(
        "ideology.Religion",
        through="ideology.IdeologyAssociation",
        related_name="ideologies",
        blank=True,
        verbose_name=_("Associated Religions"),
        help_text=_("Religions linked to this ideology."),
    )
    tags = models.ManyToManyField(
        "ideology.Tag",
        through="ideology.IdeologyTag",
        related_name="ideologies",
        blank=True,
        verbose_name=_("Tags"),
        help_text=_("Tags associated with this ideology."),
    )

    objects = IdeologyManager()

    class Meta:
        verbose_name = _("Ideology")
        verbose_name_plural = _("Ideologies")

    def get_mapped_for_calculation(self) -> Dict[str, CalculationItem]:
        return {**self._map_axis_definitions(), **self._map_conditioner_definitions()}

    def _map_axis_definitions(self) -> Dict[str, CalculationItem]:
        definitions = self.axis_definitions.select_related(
            "axis", "axis__section", "axis__section__abstraction_complexity"
        ).all()

        return {
            definition.axis.uuid.hex: format_mapped_item(
                item_type="axis",
                value=definition.value,
                complexity_uuid=definition.axis.section.abstraction_complexity.uuid.hex,
                is_indifferent=definition.is_indifferent,
                section_uuid=definition.axis.section.uuid.hex,
                margin_left=definition.margin_left or 0,
                margin_right=definition.margin_right or 0,
            )
            for definition in definitions
        }

    def _map_conditioner_definitions(self) -> Dict[str, CalculationItem]:
        definitions = self.conditioner_definitions.select_related(
            "conditioner"
        ).annotate(
            inferred_complexity=get_conditioner_complexity_annotation("conditioner")
        )

        return {
            definition.conditioner.uuid.hex: format_mapped_item(
                item_type="conditioner",
                value=definition.answer,
                complexity_uuid=(
                    definition.inferred_complexity.hex
                    if definition.inferred_complexity
                    else None
                ),
                is_indifferent=definition.is_indifferent_answer,
            )
            for definition in definitions
        }
