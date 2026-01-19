from unittest.mock import patch

from core.api.api_test_helpers import APITestBase
from core.exceptions.user_exceptions import UserDisabledException
from core.factories import UserFactory
from core.models import User
from django.urls import reverse
from rest_framework import status


class AuthTokenObtainPairViewTestCase(APITestBase):
    url = reverse("login")

    def test_login_scenarios(self):
        self.client.credentials()
        password = "strong_password_123"
        user = UserFactory(password=password)

        scenarios = [
            (
                "Success Username",
                {"username": user.username, "password": password},
                status.HTTP_200_OK,
                True,
            ),
            (
                "Success Email",
                {"username": user.email, "password": password},
                status.HTTP_200_OK,
                True,
            ),
            (
                "Fail Bad Password",
                {"username": user.username, "password": "wrong"},
                status.HTTP_401_UNAUTHORIZED,
                False,
            ),
            (
                "Fail Non Existent",
                {"username": "ghost", "password": "pwd"},
                status.HTTP_401_UNAUTHORIZED,
                False,
            ),
        ]

        for name, payload, expected_status, check_body in scenarios:
            with self.subTest(name=name):
                response = self.client.post(self.url, data=payload)
                self.assertEqual(response.status_code, expected_status)

                if check_body and expected_status == status.HTTP_200_OK:
                    self.assertIn("access", response.data)
                    self.assertIn("refresh", response.data)
                    self.assertIn("user", response.data)
                    self.assertEqual(response.data["user"]["uuid"], user.uuid.hex)


class RegisterViewTestCase(APITestBase):
    url = reverse("core:register")

    def setUp(self):
        super().setUp()
        self.valid_payload = {
            "email": "foo@foo.com",
            "password": "ThisIsARealValidPassword123!",
        }

    @patch("core.models.user.User.send_verification_email")
    def test_register_scenarios(self, mock_send_email):
        existing_email = "exists@test.com"
        UserFactory(email=existing_email)

        scenarios = [
            (
                "Success",
                self.valid_payload,
                status.HTTP_201_CREATED,
                "access",
            ),
            (
                "Fail Duplicate Email",
                {**self.valid_payload, "email": existing_email},
                status.HTTP_400_BAD_REQUEST,
                "email",
            ),
            (
                "Fail Weak Password",
                {
                    **self.valid_payload,
                    "email": "unique_weak@test.com",
                    "password": "123",
                },
                status.HTTP_400_BAD_REQUEST,
                "password",
            ),
        ]

        for name, payload, expected_status, expected_key in scenarios:
            with self.subTest(name=name):
                mock_send_email.reset_mock()

                if name == "Success":
                    User.objects.filter(email=self.valid_payload["email"]).delete()

                response = self.client.post(self.url, data=payload)
                self.assertEqual(response.status_code, expected_status)
                self.assertIn(expected_key, response.data)

                if name == "Success":
                    self.assertTrue(
                        User.objects.filter(email=payload["email"]).exists()
                    )
                    mock_send_email.assert_called_once()


class GoogleLoginViewTestCase(APITestBase):
    url = reverse("core:google-login")

    @patch("core.models.managers.user_managers.CustomUserManager.login_with_google")
    def test_google_login_success(self, mock_login):
        self.client.credentials()
        user = UserFactory()
        mock_login.return_value = user

        response = self.client.post(self.url, data={"token": "valid_token"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("user", response.data)
        mock_login.assert_called_once_with("valid_token")

    @patch("core.models.managers.user_managers.CustomUserManager.login_with_google")
    def test_google_login_invalid_token(self, mock_login):
        self.client.credentials()
        mock_login.side_effect = ValueError("Invalid Token")

        response = self.client.post(self.url, data={"token": "bad_token"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("core.models.managers.user_managers.CustomUserManager.login_with_google")
    def test_google_login_disabled_user(self, mock_login):
        self.client.credentials()
        mock_login.side_effect = UserDisabledException()

        response = self.client.post(self.url, data={"token": "disabled_user_token"})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class VerifyUserViewTestCase(APITestBase):
    def test_verify_user_scenarios(self):
        user_pending = UserFactory(is_verified=False)
        UserFactory(is_verified=True, verification_uuid=None)

        scenarios = [
            ("Success", user_pending.verification_uuid, status.HTTP_200_OK),
            (
                "Fail Invalid UUID",
                "00000000-0000-0000-0000-000000000000",
                status.HTTP_404_NOT_FOUND,
            ),
            (
                "Fail Already Verified",
                "random-uuid-but-404-logic",
                status.HTTP_404_NOT_FOUND,
            ),
        ]

        for name, uuid_val, expected_status in scenarios:
            with self.subTest(name=name):
                url = reverse(
                    "core:verify_user", kwargs={"verification_uuid": uuid_val}
                )
                response = self.client.patch(url)
                self.assertEqual(response.status_code, expected_status)

        user_pending.refresh_from_db()
        self.assertTrue(user_pending.is_verified)


class PasswordResetRequestViewTestCase(APITestBase):
    url = reverse("core:password-reset-request")

    @patch("core.models.user.User.initiate_password_reset")
    def test_password_reset_request_success(self, mock_initiate):
        self.client.credentials()
        user = UserFactory(email="reset@test.com")

        response = self.client.post(self.url, data={"email": user.email})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        mock_initiate.assert_called_once()

    @patch("core.models.user.User.initiate_password_reset")
    def test_password_reset_request_unknown_email(self, mock_initiate):
        self.client.credentials()

        response = self.client.post(self.url, data={"email": "unknown@test.com"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_initiate.assert_not_called()


class PasswordResetConfirmationFlowTestCase(APITestBase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.user.initiate_password_reset()
        self.user.refresh_from_db()
        self.reset_uuid = self.user.reset_password_uuid.hex
        self.verify_url = reverse(
            "core:password-reset-verify-token", kwargs={"uuid": self.reset_uuid}
        )
        self.confirm_url = reverse(
            "core:password-reset-confirm", kwargs={"uuid": self.reset_uuid}
        )

    def test_verify_token_success(self):
        self.client.credentials()
        response = self.client.get(self.verify_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_verify_token_invalid(self):
        self.client.credentials()
        url = reverse(
            "core:password-reset-verify-token",
            kwargs={"uuid": "00000000-0000-0000-0000-000000000000"},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_confirm_reset_success(self):
        self.client.credentials()
        new_pass = "NewStrongPass1!"
        response = self.client.post(self.confirm_url, data={"new_password": new_pass})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_pass))
        self.assertIsNone(self.user.reset_password_uuid)

    def test_confirm_reset_weak_password(self):
        self.client.credentials()
        response = self.client.post(self.confirm_url, data={"new_password": "123"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)

    def test_confirm_reset_invalid_token(self):
        self.client.credentials()
        url = reverse(
            "core:password-reset-confirm",
            kwargs={"uuid": "00000000-0000-0000-0000-000000000000"},
        )
        response = self.client.post(url, data={"new_password": "Pass!"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
