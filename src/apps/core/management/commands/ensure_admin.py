from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creates a superuser if it doesn't exist, using Django settings"

    def handle(self, *args, **options):
        User = get_user_model()
        username = settings.SUPERUSER_USERNAME
        email = settings.SUPERUSER_EMAIL
        password = settings.SUPERUSER_PASSWORD

        if not all([username, email, password]):
            self.stdout.write(
                self.style.WARNING(
                    "Missing superuser configuration in settings. Skipping admin creation."
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
