import logging
import uuid
from typing import Any

import requests
from core.exceptions.user_exceptions import UserDisabledException
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.db import transaction
from django.utils.translation import get_language
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
        if not kwargs.get("username") and not defaults.get("username"):
            defaults["username"] = self._generate_unique_username()
        return self.get_queryset().get_or_create(defaults=defaults, **kwargs)

    def create_user(self, email, password, username=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        if not username:
            username = self._generate_unique_username()
        if extra_fields.get("auth_provider") != "google":
            extra_fields.setdefault("verification_uuid", uuid.uuid4())
        with transaction.atomic():
            user = self.model(email=email, username=username, **extra_fields)
            user.set_password(password)
            user.save()
            logger.info("User with mail '%s' registered", email)
            return user

    def create_superuser(self, email, password, username=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)
        if not extra_fields.get("is_staff"):
            raise ValueError(_("Superuser must have is_staff=True."))
        if not extra_fields.get("is_superuser"):
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, username, **extra_fields)

    def register(self, user_data: dict):
        username = user_data.pop("username", None)
        email = user_data.get("email")
        password = user_data.get("password")
        user_data["preferred_language"] = get_language()
        user_data["auth_provider"] = self.model.AuthProvider.INTERNAL

        user = self.create_user(
            username=username,
            email=email,
            password=password,
            **{k: v for k, v in user_data.items() if k not in ["email", "password"]},
        )

        user.send_verification_email()
        return user

    def login_with_google(self, token: str):
        user, _ = self.get_or_create_from_google_token(token)

        if not user.is_active:
            logger.warning("Disabled user '%s' tried to login via Google", user)
            raise UserDisabledException(user)

        return user

    def get_or_create_from_google_token(self, token: str):
        user_data = self._fetch_google_user_data(token)
        return self._provision_google_user(user_data)

    def _fetch_google_user_data(self, token: str) -> dict[str, str]:
        try:
            return self._validate_google_id_token(token)
        except ValueError:
            return self._validate_google_access_token(token)

    @staticmethod
    def _validate_google_id_token(token: str) -> dict[str, str]:
        id_info = id_token.verify_oauth2_token(
            token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
        )
        return {
            "email": id_info.get("email"),
            "given_name": id_info.get("given_name", ""),
            "family_name": id_info.get("family_name", ""),
        }

    @staticmethod
    def _validate_google_access_token(token: str) -> dict[str, str]:
        try:
            response = requests.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5,
            )
            if not response.ok:
                logger.warning("Google UserInfo failed: %s", response.text)
                raise ValueError("Invalid Google Token.")
            google_info = response.json()
            return {
                "email": google_info.get("email"),
                "given_name": google_info.get("given_name", ""),
                "family_name": google_info.get("family_name", ""),
            }
        except Exception as exc:
            logger.error("Error verifying Access Token: %s", exc)
            raise ValueError("Invalid Google Token.") from exc

    def _provision_google_user(self, google_data: dict[str, Any]):
        email = google_data.get("email")
        if not email:
            raise ValueError(_("Google token has no email."))

        first_name = google_data.get("given_name", "")
        last_name = google_data.get("family_name", "")

        with transaction.atomic():
            user, created = self.get_or_create(
                email=email,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "is_verified": True,
                    "auth_provider": self.model.AuthProvider.GOOGLE,
                    "verification_uuid": uuid.uuid4(),
                },
            )

            if created:
                self._send_welcome_email(user)

            return user, created

    @staticmethod
    def _send_welcome_email(user):
        from core.tasks import send_email_notification

        logger.info("User '%s' registered via Google", user.email)
        transaction.on_commit(
            lambda: send_email_notification.delay(
                to_email=user.email,
                template_name="register_google",
                language=user.preferred_language,
                context={
                    "verification_token": user.verification_uuid.hex,
                    "name": user.first_name,
                },
            )
        )
