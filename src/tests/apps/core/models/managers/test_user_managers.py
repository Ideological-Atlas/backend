import uuid
from unittest.mock import Mock, patch

from core.exceptions.user_exceptions import UserDisabledException
from core.factories import VerifiedUserFactory
from core.models import User
from django.test import TestCase
from django.utils import translation
from django.utils.translation import gettext_lazy as _


class UserManagerBasicTestCase(TestCase):
    def test_create_user_validations(self):
        user = User.objects.create_user("ok@test.com", "pass", "user_ok")
        self.assertEqual(user.email, "ok@test.com")
        self.assertEqual(user.auth_provider, User.AuthProvider.INTERNAL)
        self.assertIsNotNone(user.verification_uuid)
        with self.assertRaises(ValueError):
            User.objects.create_user("", "pass", "user_fail")

    def test_create_user_google_provider_skips_verification_uuid(self):
        user = User.objects.create_user(
            "google@test.com",
            "pass",
            "user_google",
            auth_provider=User.AuthProvider.GOOGLE,
        )
        self.assertEqual(user.email, "google@test.com")
        self.assertEqual(user.auth_provider, User.AuthProvider.GOOGLE)
        self.assertIsNone(user.verification_uuid)

    def test_create_superuser_validations(self):
        scenarios = [
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
        for name, kwargs, message in scenarios:
            with self.subTest(name):
                with self.assertRaisesMessage(ValueError, str(message)):
                    User.objects.create_superuser(
                        "admin@t.com", "pass", "admin", **kwargs
                    )

    @patch("core.models.managers.user_managers.uuid.uuid4")
    def test_username_generation_collision(self, mock_uuid):
        original_username = "1111111111"
        User.objects.create(email="old@test.com", username=original_username)
        collision_uuid = uuid.UUID("11111111-1111-1111-1111-111111111111")
        success_uuid = uuid.UUID("22222222-2222-2222-2222-222222222222")
        verification_token = uuid.UUID("00000000-0000-0000-0000-000000000000")
        mock_uuid.side_effect = [collision_uuid, success_uuid, verification_token]
        user = User.objects.create_user(
            email="new@test.com", password="pwd", username=None
        )
        self.assertEqual(user.username, success_uuid.hex[:10])
        self.assertEqual(user.verification_uuid, verification_token)

    def test_get_or_create_generates_username_if_missing(self):
        user_one, _ = User.objects.get_or_create(
            email="u1@test.com", username="explicit_user"
        )
        self.assertEqual(user_one.username, "explicit_user")
        user_two, _ = User.objects.get_or_create(
            email="u2@test.com", defaults={"username": "default_user"}
        )
        self.assertEqual(user_two.username, "default_user")
        user_three, _ = User.objects.get_or_create(email="u3@test.com")
        self.assertIsNotNone(user_three.username)
        self.assertEqual(len(user_three.username), 10)

    @patch("core.models.managers.user_managers.get_language")
    @patch("core.models.managers.user_managers.CustomUserManager.create_user")
    def test_register_flow(self, mock_create_user, mock_get_language):
        mock_get_language.return_value = "fr"
        mock_user_instance = Mock()
        mock_create_user.return_value = mock_user_instance

        data = {"email": "test@test.com", "password": "pass", "username": "user"}
        User.objects.register(data)

        mock_create_user.assert_called_once()
        self.assertEqual(mock_create_user.call_args[1]["preferred_language"], "fr")
        mock_user_instance.send_verification_email.assert_called_once()


class GoogleAuthManagerTestCase(TestCase):
    @patch("core.tasks.send_email_notification.delay")
    @patch("core.models.managers.user_managers.id_token.verify_oauth2_token")
    def test_google_token_strategy_id_token_success(self, mock_verify_jwt, mock_send):
        mock_verify_jwt.return_value = {
            "email": "jwt@test.com",
            "given_name": "JWT",
            "family_name": "User",
        }
        with self.captureOnCommitCallbacks(execute=True):
            user, created = User.objects.get_or_create_from_google_token(
                "valid_jwt_token"
            )
        self.assertTrue(created)
        self.assertEqual(user.email, "jwt@test.com")
        self.assertTrue(user.is_verified)

        mock_send.assert_called_once()
        self.assertEqual(mock_send.call_args.kwargs["template_name"], "register_google")

    @patch("core.tasks.send_email_notification.delay")
    @patch("core.models.managers.user_managers.requests.get")
    @patch("core.models.managers.user_managers.id_token.verify_oauth2_token")
    def test_google_token_strategy_fallback_to_access_token(
        self, mock_verify_jwt, mock_requests, mock_send
    ):
        mock_verify_jwt.side_effect = ValueError("Wrong number of segments")
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "email": "access@test.com",
            "given_name": "Access",
            "family_name": "Token",
        }
        mock_requests.return_value = mock_response
        with self.captureOnCommitCallbacks(execute=True):
            user, created = User.objects.get_or_create_from_google_token(
                "valid_access_token"
            )
        self.assertTrue(created)
        self.assertEqual(user.email, "access@test.com")
        mock_verify_jwt.assert_called_once()
        mock_requests.assert_called_once()

    @patch("core.models.managers.user_managers.requests.get")
    @patch("core.models.managers.user_managers.id_token.verify_oauth2_token")
    def test_google_token_both_strategies_fail(self, mock_verify_jwt, mock_requests):
        mock_verify_jwt.side_effect = ValueError("Not a JWT")
        mock_response = Mock()
        mock_response.ok = False
        mock_response.text = "Bad Token"
        mock_requests.return_value = mock_response
        with self.assertRaisesMessage(ValueError, "Invalid Google Token"):
            User.objects.get_or_create_from_google_token("invalid_token")

    @patch("core.models.managers.user_managers.requests.get")
    @patch("core.models.managers.user_managers.id_token.verify_oauth2_token")
    def test_google_token_network_error(self, mock_verify_jwt, mock_requests):
        mock_verify_jwt.side_effect = ValueError("Not a JWT")
        mock_requests.side_effect = Exception("Connection Timeout")

        with self.assertRaisesMessage(ValueError, "Invalid Google Token"):
            User.objects.get_or_create_from_google_token("timeout_token")

    @patch("core.models.managers.user_managers.id_token.verify_oauth2_token")
    def test_google_token_no_email_in_payload(self, mock_verify_jwt):
        mock_verify_jwt.return_value = {"sub": "12345", "given_name": "NoEmail"}

        with translation.override("en"):
            with self.assertRaisesMessage(ValueError, "Google token has no email"):
                User.objects.get_or_create_from_google_token("token_no_email")

    @patch("core.tasks.send_email_notification.delay")
    @patch("core.models.managers.user_managers.id_token.verify_oauth2_token")
    def test_google_provisioning_existing_user_skips_email(
        self, mock_verify_jwt, mock_send
    ):
        existing_email = "existing@test.com"
        User.objects.create(email=existing_email, username="old_user")

        mock_verify_jwt.return_value = {
            "email": existing_email,
            "given_name": "Old",
            "family_name": "User",
        }

        with self.captureOnCommitCallbacks(execute=True):
            user, created = User.objects.get_or_create_from_google_token("token")
        self.assertFalse(created)
        self.assertEqual(user.email, existing_email)
        mock_send.assert_not_called()

    @patch(
        "core.models.managers.user_managers.CustomUserManager.get_or_create_from_google_token"
    )
    def test_login_interface_success(self, mock_get_google):
        user = VerifiedUserFactory.build(is_active=True)
        mock_get_google.return_value = (user, False)

        result = User.objects.login_with_google("token")
        self.assertEqual(result, user)

    @patch(
        "core.models.managers.user_managers.CustomUserManager.get_or_create_from_google_token"
    )
    def test_login_interface_disabled_user(self, mock_get_google):
        user = VerifiedUserFactory.build(is_active=False)
        mock_get_google.return_value = (user, False)

        with self.assertRaises(UserDisabledException):
            User.objects.login_with_google("token")
