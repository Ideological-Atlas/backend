import logging
from typing import Optional

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

    email = models.EmailField(_("email address"), unique=True)
    preferred_language = models.CharField(max_length=10, default="es")
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

    def send_verification_email(self, language: Optional[str] = None) -> None:
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
