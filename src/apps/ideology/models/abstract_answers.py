from core.models import TimeStampedUUIDModel
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseAxisAnswer(TimeStampedUUIDModel):
    axis = models.ForeignKey(
        "ideology.IdeologyAxis",
        on_delete=models.CASCADE,
        verbose_name=_("Axis"),
        help_text=_("The specific axis being measured."),
    )
    is_indifferent = models.BooleanField(
        default=False,
        verbose_name=_("Is Indifferent"),
        help_text=_("If true, the value is irrelevant/indifferent."),
    )
    value = models.IntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(-100),
            MaxValueValidator(100),
        ],
        verbose_name=_("Position Value"),
    )
    margin_left = models.IntegerField(
        default=0,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(200),
        ],
        verbose_name=_("Left Margin Tolerance"),
    )
    margin_right = models.IntegerField(
        default=0,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(200),
        ],
        verbose_name=_("Right Margin Tolerance"),
    )

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        if self.is_indifferent:
            self.value = None
            self.margin_left = None
            self.margin_right = None
        elif self.value is None:
            raise ValidationError(
                _("A non-indifferent answer must have a numeric value.")
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class BaseConditionerAnswer(TimeStampedUUIDModel):
    conditioner = models.ForeignKey(
        "ideology.IdeologyConditioner",
        on_delete=models.CASCADE,
        verbose_name=_("Conditioner"),
        help_text=_("The question or variable being answered."),
    )
    answer = models.CharField(
        max_length=255,
        verbose_name=_("Answer"),
    )

    class Meta:
        abstract = True
