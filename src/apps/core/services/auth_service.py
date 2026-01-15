import logging
from typing import Optional

from core.models import User
from core.tasks import send_email_notification
from django.utils.translation import get_language

logger = logging.getLogger(__name__)


class AuthService:
    @staticmethod
    def register_user(user_data: dict) -> User:
        username = user_data.pop("username", None)
        email = user_data.get("email")
        password = user_data.get("password")
        user_data["preferred_language"] = get_language()
        user_data["auth_provider"] = User.AuthProvider.INTERNAL

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **{k: v for k, v in user_data.items() if k not in ["email", "password"]}
        )

        AuthService.trigger_verification_email(user)

        return user

    @staticmethod
    def trigger_verification_email(user: User, language: Optional[str] = None) -> None:
        if user.is_verified:
            logger.warning(
                "Attempted to trigger email verification for already verified user '%s'",
                user,
            )
            return

        target_language = language or user.preferred_language

        logger.debug("Triggering email verification for '%s'", user)

        send_email_notification.delay(
            to_email=user.email,
            template_name="register",
            language=target_language,
            context={"verification_token": user.verification_uuid.hex},
        )

        logger.debug("Email verification was sent to '%s'", user)
