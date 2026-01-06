from core.models import TimeStampedUUIDModel
from django.db import models
from django.utils.translation import gettext_lazy as _
from ideology.models import Ideology, Tag


class IdeologyTag(TimeStampedUUIDModel):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name="ideology_assignments",
        verbose_name=_("Tag"),
        help_text=_("The specific tag to associate with the ideology."),
    )
    ideology = models.ForeignKey(
        Ideology,
        on_delete=models.CASCADE,
        related_name="tag_assignments",
        verbose_name=_("Ideology"),
        help_text=_("The ideology to which this tag belongs."),
    )

    class Meta:
        verbose_name = _("Ideology tag")
        verbose_name_plural = _("Ideology tags")
        unique_together = ["tag", "ideology"]
