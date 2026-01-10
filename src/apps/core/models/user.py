import logging

from core.exceptions.user_exceptions import UserAlreadyVerifiedException
from core.models.managers import CustomUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from .abstract import TimeStampedUUIDModel

logger = logging.getLogger(__name__)


class User(AbstractUser, TimeStampedUUIDModel, PermissionsMixin):
    class AuthProvider(models.TextChoices):
        INTERNAL = "internal", _("Internal")
        GOOGLE = "google", _("Google")

    email = models.EmailField(_("email address"), unique=True)
    preferred_language = models.CharField(max_length=10, default="es")

    is_verified = models.BooleanField(
        default=False,
        verbose_name=_("Is verified"),
        help_text=_("Field that shows if the user is verified or not."),
    )

    auth_provider = models.CharField(
        max_length=20,
        choices=AuthProvider.choices,
        default=AuthProvider.INTERNAL,
        verbose_name=_("Auth Provider"),
        help_text=_("The provider used for the user authentication/registration."),
    )

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.username

    def verify(self):
        if self.is_verified:
            logger.warning("User '%s' is already verified", self)
            raise UserAlreadyVerifiedException(self)

        logger.info("User '%s' was verified", self)
        self.is_verified = True
        self.save()

    def trigger_email_verification(self, language: str | None = None):
        from core.tasks import send_email_notification

        if self.is_verified:
            logger.warning(
                "Attempted to trigger email verification for already verified user '%s'",
                self,
            )
            return

        target_language = language or self.preferred_language

        logger.debug("Triggering email verification for '%s'", self)
        send_email_notification.delay(
            to_email=self.email,
            template_name="register",
            language=target_language,
            context={"user_uuid": str(self.uuid)},
        )
        logger.debug("Email verification was sent to '%s'", self)

    def generate_completed_answer(self):
        from ideology.models import (
            AxisAnswer,
            CompletedAnswer,
            ConditionerAnswer,
            IdeologyAbstractionComplexity,
        )

        axis_answers = (
            AxisAnswer.objects.filter(user=self)
            .select_related(
                "axis", "axis__section", "axis__section__abstraction_complexity"
            )
            .order_by("axis__section__name")
        )

        conditioner_answers = (
            ConditionerAnswer.objects.filter(user=self)
            .select_related("conditioner", "conditioner__abstraction_complexity")
            .order_by("conditioner__name")
        )

        complexities = IdeologyAbstractionComplexity.objects.all().order_by(
            "complexity"
        )

        structured_data = []

        for complexity in complexities:
            complexity_data = {
                "level": complexity.name,
                "complexity": complexity.complexity,
                "sections": [],
                "conditioners": [],
            }

            complexity_axes = [
                axis_answer
                for axis_answer in axis_answers
                if axis_answer.axis.section.abstraction_complexity_id == complexity.id
            ]

            sections_map = {}
            for complexity_axis in complexity_axes:
                section_name = complexity_axis.axis.section.name
                if section_name not in sections_map:
                    sections_map[section_name] = {
                        "name": section_name,
                        "description": complexity_axis.axis.section.description,
                        "axes": [],
                    }

                sections_map[section_name]["axes"].append(
                    {
                        "name": complexity_axis.axis.name,
                        "value": int(complexity_axis.value),
                        "left_label": complexity_axis.axis.left_label,
                        "right_label": complexity_axis.axis.right_label,
                    }
                )

            complexity_data["sections"] = list(sections_map.values())

            complexity_conditioners = [
                complexity_conditioner
                for complexity_conditioner in conditioner_answers
                if complexity_conditioner.conditioner.abstraction_complexity_id
                == complexity.id
            ]

            for conditioner in complexity_conditioners:
                complexity_data["conditioners"].append(
                    {
                        "name": conditioner.conditioner.name,
                        "answer": conditioner.answer,
                        "type": conditioner.conditioner.type,
                    }
                )

            structured_data.append(complexity_data)

        return CompletedAnswer.objects.create(
            completed_by=self, answers=structured_data
        )
