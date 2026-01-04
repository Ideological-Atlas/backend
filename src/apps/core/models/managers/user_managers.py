import logging
import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class CustomUserManager(BaseUserManager):

    def _generate_unique_username(self):
        while True:
            username = f"{uuid.uuid4().hex[:10]}"
            if not self.model.objects.filter(username=username).exists():
                return username

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

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, username, **extra_fields)
