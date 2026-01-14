import os
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

User = get_user_model()


class EnsureAdminCommandTestCase(TestCase):
    def call_command_silent(self):
        out = StringIO()
        call_command("ensure_admin", stdout=out)
        return out.getvalue()

    def test_ensure_admin_scenarios(self):
        scenarios = [
            (
                "Create Success",
                {
                    "SUPERUSER_USERNAME": "adm_new",
                    "SUPERUSER_MAIL": "n@ex.com",
                    "SUPERUSER_PASSWORD": "123",
                },
                "created successfully",
                True,
            ),
            (
                "Already Exists",
                {
                    "SUPERUSER_USERNAME": "adm_ex",
                    "SUPERUSER_MAIL": "e@ex.com",
                    "SUPERUSER_PASSWORD": "123",
                },
                "already exists",
                False,
            ),
            ("Missing Vars", {}, "Missing superuser environment variables", False),
        ]
        User.objects.create_superuser("e@ex.com", "123", "adm_ex")
        for name, env_vars, expected_msg, should_create in scenarios:
            with self.subTest(name):
                with patch.dict(os.environ, {}, clear=True):
                    with patch.dict(os.environ, env_vars):
                        output = self.call_command_silent()
                        self.assertIn(expected_msg, output)
                        if name == "Create Success":
                            self.assertTrue(
                                User.objects.filter(
                                    username=env_vars["SUPERUSER_USERNAME"]
                                ).exists()
                            )
