from core.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from ideology.models.managers import UserConditionerAnswerManager

from .abstract_answers import BaseConditionerAnswer


class UserConditionerAnswer(BaseConditionerAnswer):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="conditioner_answers",
        verbose_name=_("User"),
    )

    objects = UserConditionerAnswerManager()

    class Meta:
        verbose_name = _("User Conditioner Answer")
        verbose_name_plural = _("User Conditioner Answers")
        unique_together = ["user", "conditioner"]

    def __str__(self):
        return f"{self.user.username} - {self.conditioner.name}: {self.answer}"
