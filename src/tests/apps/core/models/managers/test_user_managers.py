from unittest.mock import patch

from core.models import User
from django.test import TestCase


class UserManagerTestCase(TestCase):
    def test_create_user_validations(self):
        u = User.objects.create_user("ok@test.com", "pass", "user_ok")
        self.assertEqual(u.email, "ok@test.com")

        with self.assertRaises(ValueError):
            User.objects.create_user("", "pass", "user_fail")

    def test_create_superuser_validations(self):
        cases = [
            (
                "No Staff",
                {"is_staff": False, "is_superuser": True},
                "Superuser must have is_staff=True.",
            ),
            (
                "No Super",
                {"is_staff": True, "is_superuser": False},
                "Superuser must have is_superuser=True.",
            ),
        ]

        for name, kwargs, msg in cases:
            with self.subTest(name):
                with self.assertRaisesMessage(ValueError, msg):
                    User.objects.create_superuser(
                        "admin@t.com", "pass", "admin", **kwargs
                    )

    @patch("core.models.managers.user_managers.uuid.uuid4")
    def test_username_generation_collision(self, mock_uuid):
        User.objects.create(email="old@test.com", username="1111111111")

        class MockHex:
            def __init__(self, h):
                self.hex = h

        mock_uuid.side_effect = [MockHex("1111111111"), MockHex("2222222222")]

        user = User.objects.create_user(
            email="new@test.com", password="pwd", username=None  # nosec
        )
        self.assertEqual(user.username, "2222222222")
