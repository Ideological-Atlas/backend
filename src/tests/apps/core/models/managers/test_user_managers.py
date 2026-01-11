from unittest.mock import Mock, patch

from core.models import User
from django.test import TestCase
from django.utils import translation
from django.utils.translation import gettext_lazy as _


class UserManagerTestCase(TestCase):
    def test_create_user_validations(self):
        u = User.objects.create_user("ok@test.com", "pass", "user_ok")
        self.assertEqual(u.email, "ok@test.com")
        self.assertEqual(u.auth_provider, User.AuthProvider.INTERNAL)

        with self.assertRaises(ValueError):
            User.objects.create_user("", "pass", "user_fail")

    def test_create_superuser_validations(self):
        cases = [
            (
                "No Staff",
                {"is_staff": False, "is_superuser": True},
                _("Superuser must have is_staff=True."),
            ),
            (
                "No Super",
                {"is_staff": True, "is_superuser": False},
                _("Superuser must have is_superuser=True."),
            ),
        ]

        for name, kwargs, msg in cases:
            with self.subTest(name):
                with self.assertRaisesMessage(ValueError, str(msg)):
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

    def test_get_or_create_generates_username_if_missing(self):
        user1, _ = User.objects.get_or_create(
            email="u1@test.com", username="explicit_user"
        )
        self.assertEqual(user1.username, "explicit_user")

        user2, _ = User.objects.get_or_create(
            email="u2@test.com", defaults={"username": "default_user"}
        )
        self.assertEqual(user2.username, "default_user")

        user3, _ = User.objects.get_or_create(email="u3@test.com")
        self.assertIsNotNone(user3.username)
        self.assertEqual(len(user3.username), 10)

    @patch("core.tasks.send_email_notification.delay")
    @patch("core.models.managers.user_managers.id_token.verify_oauth2_token")
    def test_get_or_create_from_google_id_token_jwt_success(
        self, mock_verify, mock_send
    ):
        mock_verify.return_value = {
            "email": "jwt@test.com",
            "given_name": "JWT",
            "family_name": "User",
        }

        user, created = User.objects.get_or_create_from_google_token("valid_jwt_token")

        self.assertTrue(created)
        self.assertEqual(user.email, "jwt@test.com")
        self.assertEqual(user.auth_provider, User.AuthProvider.GOOGLE)
        self.assertTrue(user.is_verified)

        mock_send.assert_called_once()
        self.assertEqual(mock_send.call_args.kwargs["template_name"], "register_google")
        self.assertEqual(mock_send.call_args.kwargs["to_email"], "jwt@test.com")

    @patch("core.tasks.send_email_notification.delay")
    @patch("core.models.managers.user_managers.requests.get")
    @patch("core.models.managers.user_managers.id_token.verify_oauth2_token")
    def test_get_or_create_from_google_access_token_success(
        self, mock_verify, mock_requests, mock_send
    ):
        mock_verify.side_effect = ValueError("Wrong number of segments")
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "email": "access@test.com",
            "given_name": "Access",
            "family_name": "Token",
        }
        mock_requests.return_value = mock_response

        user, created = User.objects.get_or_create_from_google_token(
            "valid_access_token"
        )

        self.assertTrue(created)
        self.assertEqual(user.email, "access@test.com")
        mock_verify.assert_called_once()
        mock_requests.assert_called_once()
        mock_send.assert_called_once()

    @patch("core.models.managers.user_managers.requests.get")
    @patch("core.models.managers.user_managers.id_token.verify_oauth2_token")
    def test_get_or_create_failure_both_methods(self, mock_verify, mock_requests):
        mock_verify.side_effect = ValueError("Wrong number of segments")
        mock_response = Mock()
        mock_response.ok = False
        mock_response.text = "Bad Token"
        mock_requests.return_value = mock_response
        with self.assertRaisesMessage(ValueError, "Invalid Google Token"):
            User.objects.get_or_create_from_google_token("invalid_token")

    @patch("core.models.managers.user_managers.id_token.verify_oauth2_token")
    def test_get_or_create_from_google_token_no_email(self, mock_verify):
        mock_verify.return_value = {"sub": "12345"}

        with translation.override("en"):
            with self.assertRaisesMessage(ValueError, "Google token has no email"):
                User.objects.get_or_create_from_google_token("token_no_email")
