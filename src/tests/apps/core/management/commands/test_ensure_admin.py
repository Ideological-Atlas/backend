from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings

User = get_user_model()


class EnsureAdminCommandTestCase(TestCase):
    def call_command_silent(self):
        out = StringIO()
        call_command("ensure_admin", stdout=out)
        return out.getvalue()

    @override_settings(
        SUPERUSER_USERNAME="adm_new",
        SUPERUSER_EMAIL="n@ex.com",
        SUPERUSER_PASSWORD="123",
    )
    def test_ensure_admin_create_success(self):
        output = self.call_command_silent()
        self.assertIn("created successfully", output)
        self.assertTrue(User.objects.filter(username="adm_new").exists())

    @override_settings(
        SUPERUSER_USERNAME="adm_ex",
        SUPERUSER_EMAIL="e@ex.com",
        SUPERUSER_PASSWORD="123",
    )
    def test_ensure_admin_already_exists(self):
        User.objects.create_superuser("e@ex.com", "123", "adm_ex")
        output = self.call_command_silent()
        self.assertIn("already exists", output)

    @override_settings(
        SUPERUSER_USERNAME=None, SUPERUSER_EMAIL=None, SUPERUSER_PASSWORD=None
    )
    def test_ensure_admin_missing_vars(self):
        output = self.call_command_silent()
        self.assertIn("Missing superuser configuration", output)
