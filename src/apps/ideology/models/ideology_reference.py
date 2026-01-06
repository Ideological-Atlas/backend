from core.models import TimeStampedUUIDModel
from django.db import models
from django.utils.translation import gettext_lazy as _
from ideology.models import Ideology


class IdeologyReference(TimeStampedUUIDModel):
    ideology = models.ForeignKey(
        Ideology,
        on_delete=models.CASCADE,
        related_name="references",
        verbose_name=_("Ideology"),
        help_text=_("The ideology supported or explained by this reference."),
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"),
        help_text=_(
            "The title or source name (e.g., Book Title, Article Headline, Author Name)."
        ),
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description"),
        help_text=_("Contextual details or specific quotes relevant to the ideology."),
    )
    url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("URL"),
        help_text=_("Direct link to the source material, if available online."),
    )

    class Meta:
        verbose_name = _("Ideology reference")
        verbose_name_plural = _("Ideology references")
