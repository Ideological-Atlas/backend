from core.helpers import handle_storage
from core.models.abstract import TimeStampedUUIDModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class Country(TimeStampedUUIDModel):
    name = models.CharField(
        verbose_name=_("Name"), max_length=255, unique=True, db_index=True
    )
    code2 = models.CharField(
        verbose_name=_("ISO Code (2)"), max_length=2, unique=True, blank=True, null=True
    )
    flag = models.ImageField(
        verbose_name=_("Flag"), upload_to=handle_storage, blank=True, null=True
    )

    class Meta:
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Region(TimeStampedUUIDModel):
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="regions",
        verbose_name=_("Country"),
    )
    name = models.CharField(verbose_name=_("Name"), max_length=255, db_index=True)
    flag = models.ImageField(
        verbose_name=_("Flag"), upload_to=handle_storage, blank=True, null=True
    )

    class Meta:
        verbose_name = _("Region")
        verbose_name_plural = _("Regions")
        ordering = ["country", "name"]
        unique_together = ["country", "name"]

    def __str__(self):
        code = self.country.code2 if self.country.code2 else "N/A"
        return f"{self.name} ({code})"
