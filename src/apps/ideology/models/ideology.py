from core.helpers import handle_storage
from core.models import TimeStampedUUIDModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class Ideology(TimeStampedUUIDModel):
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
        "cities_light.Country",
        through="ideology.IdeologyAssociation",
        related_name="ideologies",
        blank=True,
        verbose_name=_("Associated Countries"),
        help_text=_("Countries where this ideology is explicitly present."),
    )

    associated_regions = models.ManyToManyField(
        "cities_light.Region",
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

    class Meta:
        verbose_name = _("Ideology")
        verbose_name_plural = _("Ideologies")
