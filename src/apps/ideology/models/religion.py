from core.models import TimeStampedUUIDModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class Religion(TimeStampedUUIDModel):
    name = models.CharField(
        max_length=128,
        unique=True,
        verbose_name=_("Name"),
        help_text=_("The name of the religion or belief system."),
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description"),
        help_text=_("Brief description of the religion's core tenets."),
    )

    class Meta:
        verbose_name = _("Religion")
        verbose_name_plural = _("Religions")
        ordering = ["name"]

    def __str__(self):
        return self.name
