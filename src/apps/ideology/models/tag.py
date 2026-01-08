from core.models import TimeStampedUUIDModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class Tag(TimeStampedUUIDModel):
    name = models.CharField(
        max_length=120,
        unique=True,
        db_index=True,
        verbose_name=_("Name"),
        help_text=_("The name of the tag."),
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description"),
        help_text=_("The description of the tag."),
    )

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
