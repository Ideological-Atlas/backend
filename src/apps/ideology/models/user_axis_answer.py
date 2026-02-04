from core.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from ideology.models.managers import UserAxisAnswerManager

from .abstract_answers import BaseAxisAnswer


class UserAxisAnswer(BaseAxisAnswer):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="axis_answers",
        verbose_name=_("User"),
    )

    objects = UserAxisAnswerManager()

    class Meta:
        verbose_name = _("User Axis Answer")
        verbose_name_plural = _("User Axis Answers")
        unique_together = ["user", "axis"]

    def __str__(self):
        val = "Indifferent" if self.is_indifferent else str(self.value)
        return f"{self.user.username} - {self.axis.name}: {val}"
