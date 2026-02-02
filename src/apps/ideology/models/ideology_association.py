from core.models import TimeStampedUUIDModel
from django.db import models
from django.utils.translation import gettext_lazy as _
from ideology.models import Ideology, Religion


class IdeologyAssociation(TimeStampedUUIDModel):
    ideology = models.ForeignKey(
        Ideology,
        on_delete=models.CASCADE,
        related_name="associations",
        verbose_name=_("Ideology"),
        help_text=_("The ideology being contextualized."),
    )
    country = models.ForeignKey(
        "core.Country",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ideology_associations",
        verbose_name=_("Country"),
        help_text=_("The country where this ideology is present or relevant."),
    )
    region = models.ForeignKey(
        "core.Region",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ideology_associations",
        verbose_name=_("Region"),
        help_text=_("The specific region within a country (optional)."),
    )
    religion = models.ForeignKey(
        Religion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ideology_associations",
        verbose_name=_("Religion"),
        help_text=_("The religion associated with this ideology in this context."),
    )

    class Meta:
        verbose_name = _("Ideology Association")
        verbose_name_plural = _("Ideology Associations")
        constraints = [
            models.UniqueConstraint(
                fields=["ideology", "country", "region", "religion"],
                name="unique_ideology_context_association",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(country__isnull=False)
                    | models.Q(region__isnull=False)
                    | models.Q(religion__isnull=False)
                ),
                name="ideology_association_has_at_least_one_context",
            ),
        ]

    def __str__(self):
        parts = [self.ideology.name]
        if self.country:
            parts.append(f"in {self.country.name}")
        if self.region:
            parts.append(f"({self.region.name})")
        if self.religion:
            parts.append(f"linked to {self.religion.name}")
        return " ".join(parts)
