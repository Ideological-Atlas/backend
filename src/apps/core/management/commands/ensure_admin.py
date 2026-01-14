import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creates a superuser if it doesn't exist, strictly via environment variables"

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get("SUPERUSER_USERNAME")
        email = os.environ.get("SUPERUSER_MAIL")
        password = os.environ.get("SUPERUSER_PASSWORD")
        if not all([username, email, password]):
            self.stdout.write(
                self.style.WARNING(
                    "Missing superuser environment variables. Skipping admin creation."
                )
            )
            return
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.SUCCESS(f"Superuser '{username}' already exists.")
            )
        else:
            User.objects.create_superuser(
                username=username, email=email, password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f"Superuser '{username}' created successfully.")
            )
