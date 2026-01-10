import logging
import uuid

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

logger = logging.getLogger(__name__)


class CustomUserManager(BaseUserManager):

    def _generate_unique_username(self):
        while True:
            username = f"{uuid.uuid4().hex[:10]}"
            if not self.model.objects.filter(username=username).exists():
                return username

    def get_or_create(self, defaults=None, **kwargs):
        defaults = defaults or {}

        if not defaults.get("username"):
            defaults["username"] = self._generate_unique_username()
        return self.get_queryset().get_or_create(defaults=defaults, **kwargs)

    def create_user(self, email, password, username, **extra_fields):
        if not email:
            raise ValueError(_("The Email must be set"))

        email = self.normalize_email(email)

        if not username:
            username = self._generate_unique_username()

        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save()
        logger.info("User with mail '%s' registered", email)
        return user

    def create_superuser(self, email, password, username, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_staff"):
            raise ValueError(_("Superuser must have is_staff=True."))
        if not extra_fields.get("is_superuser"):
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, username, **extra_fields)

    def get_or_create_from_google_token(self, token: str):
        id_info = id_token.verify_oauth2_token(
            token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
        )

        email = id_info.get("email")
        if not email:
            raise ValueError(_("Google token has no email."))

        first_name = id_info.get("given_name", "")
        last_name = id_info.get("family_name", "")

        user, created = self.get_or_create(
            email=email,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "is_verified": True,
                "auth_provider": self.model.AuthProvider.GOOGLE,
            },
        )

        if created:
            user.set_unusable_password()
            user.save()
            logger.info("User '%s' registered via Google", email)

        if not user.is_verified:
            user.is_verified = True
            user.save()

        return user, created
