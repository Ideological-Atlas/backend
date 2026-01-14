import logging

from core.exceptions.user_exceptions import UserAlreadyVerifiedException
from core.models.managers import CustomUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models, transaction
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
