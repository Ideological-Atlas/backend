import logging
import uuid

import requests
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

    def get_or_create_from_google_token(self, token: str):
        try:
            id_info = id_token.verify_oauth2_token(
                token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
            )
            user_data = {
                "email": id_info.get("email"),
                "given_name": id_info.get("given_name", ""),
                "family_name": id_info.get("family_name", ""),
            }
        except ValueError:
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
                user_data = {
                    "email": google_info.get("email"),
                    "given_name": google_info.get("given_name", ""),
                    "family_name": google_info.get("family_name", ""),
                }
            except Exception as exc:
                logger.error("Error verifying Access Token: %s", exc)
                raise ValueError("Invalid Google Token.") from exc

        email = user_data.get("email")
        if not email:
            raise ValueError(_("Google token has no email."))

        first_name = user_data.get("given_name", "")
        last_name = user_data.get("family_name", "")

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
            from core.tasks import send_email_notification

            user.set_unusable_password()
            user.save()
            logger.info("User '%s' registered via Google", email)

            send_email_notification.delay(
                to_email=user.email,
                template_name="register_google",
                language=user.preferred_language,
                context={"user_uuid": str(user.uuid), "name": user.first_name},
            )

        if not user.is_verified:
            user.is_verified = True
            user.save()

        return user, created
