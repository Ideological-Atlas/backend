import logging
import uuid
from typing import Any

from core.exceptions.user_exceptions import UserAlreadyVerifiedException
from core.models.managers import CustomUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models, transaction
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from .abstract import TimeStampedUUIDModel

logger = logging.getLogger(__name__)


class User(AbstractUser, TimeStampedUUIDModel, PermissionsMixin):
    class AuthProvider(models.TextChoices):
        INTERNAL = "internal", _("Internal")
        GOOGLE = "google", _("Google")

    class Appearance(models.TextChoices):
        LIGHT = "light", _("Light")
        DARK = "dark", _("Dark")
        AUTO = "auto", _("Auto")

    email = models.EmailField(_("email address"), unique=True)
    preferred_language = models.CharField(max_length=10, default="es")
    appearance = models.CharField(
        max_length=10,
        choices=Appearance.choices,
        default=Appearance.AUTO,
        verbose_name=_("Appearance"),
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name=_("Is Public Profile"),
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_("Is verified"),
        help_text=_("Field that shows if the user is verified or not."),
    )
    verification_uuid = models.UUIDField(
        null=True,
        blank=True,
        unique=True,
        db_index=True,
        verbose_name=_("Verification UUID"),
        help_text=_("Secret token used for email verification."),
    )
    reset_password_uuid = models.UUIDField(
        null=True,
        blank=True,
        unique=True,
        db_index=True,
        verbose_name=_("Reset Password UUID"),
        help_text=_("Token used for password reset requests."),
    )
    auth_provider = models.CharField(
        max_length=20,
        choices=AuthProvider.choices,
        default=AuthProvider.INTERNAL,
        verbose_name=_("Auth Provider"),
        help_text=_("The provider used for the user authentication/registration."),
    )
    bio = models.TextField(
        null=True, blank=True, verbose_name=_("Bio"), help_text=_("User bio")
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
        with transaction.atomic():
            self.is_verified = True
            self.verification_uuid = None
            self.save()

    def send_verification_email(self, language: str | None = None) -> None:
        from core.tasks import send_email_notification

        if self.is_verified:
            logger.warning(
                "Attempted to trigger email verification for already verified user '%s'",
                self,
            )
            return

        target_language = language or self.preferred_language or get_language()

        logger.debug("Triggering email verification for '%s'", self)

        transaction.on_commit(
            lambda: send_email_notification.delay(
                to_email=self.email,
                template_name="register",
                language=target_language,
                context={"verification_token": self.verification_uuid.hex},
            )
        )

    def initiate_password_reset(self, send_notification=True):
        from core.tasks import clear_reset_password_token, send_email_notification

        new_uuid = uuid.uuid4()

        with transaction.atomic():
            self.reset_password_uuid = new_uuid
            self.save(update_fields=["reset_password_uuid"])

            def _schedule_tasks():
                if send_notification:
                    send_email_notification.delay(
                        to_email=self.email,
                        template_name="reset_password",
                        language=self.preferred_language,
                        context={"reset_token": new_uuid.hex},
                    )
                clear_reset_password_token.apply_async(args=[self.id], countdown=1800)

            transaction.on_commit(_schedule_tasks)

        logger.info(
            "Password reset initiated for user '%s' (Email sent: %s)",
            self,
            send_notification,
        )

    def get_affinity_data(self, target_data: dict[str, dict]) -> dict[str, Any]:
        from core.services.affinity_calculator import AffinityCalculator
        from ideology.models import UserAxisAnswer

        my_data = UserAxisAnswer.objects.get_mapped_for_calculation(self)
        return AffinityCalculator(my_data, target_data).calculate_detailed()

    def calculate_detailed_affinity_with(self, target_answer) -> dict[str, Any]:
        from ideology.models import (
            IdeologyAbstractionComplexity,
            IdeologyAxis,
            IdeologySection,
        )

        target_data_mapped = target_answer.get_mapped_for_calculation()
        affinity_data = self.get_affinity_data(target_data_mapped)

        complexity_uuids = set()
        section_uuids = set()
        axis_uuids = set()

        for complexity_item in affinity_data["complexities"]:
            complexity_uuids.add(complexity_item["complexity_uuid"])
            for section_item in complexity_item["sections"]:
                section_uuids.add(section_item["section_uuid"])
                for axis_item in section_item["axes"]:
                    axis_uuids.add(axis_item["axis_uuid"])

        complexities_map = {
            ideology_abstraction_complexity.uuid.hex: ideology_abstraction_complexity
            for ideology_abstraction_complexity in IdeologyAbstractionComplexity.objects.filter(
                uuid__in=complexity_uuids
            )
        }
        sections_map = {
            ideology_section.uuid.hex: ideology_section
            for ideology_section in IdeologySection.objects.filter(
                uuid__in=section_uuids
            )
        }
        axes_map = {
            ideology_axis.uuid.hex: ideology_axis
            for ideology_axis in IdeologyAxis.objects.filter(uuid__in=axis_uuids)
        }

        for complexity_item in affinity_data["complexities"]:
            complexity_item["complexity"] = complexities_map.get(
                complexity_item["complexity_uuid"]
            )

            for section_item in complexity_item["sections"]:
                section_item["section"] = sections_map.get(section_item["section_uuid"])

                for axis_item in section_item["axes"]:
                    axis_item["axis"] = axes_map.get(axis_item["axis_uuid"])

        return {
            "target_user": target_answer.completed_by,
            "total": affinity_data["total"],
            "complexities": affinity_data["complexities"],
        }
