from unittest.mock import patch

from core.api.api_test_helpers import APITestBase
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

    @patch("core.services.AuthService.trigger_verification_email")
    def test_register_scenarios(self, mock_trigger):
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
                mock_trigger.reset_mock()

                if name == "Success":
                    User.objects.filter(email=self.valid_payload["email"]).delete()

                response = self.client.post(self.url, data=payload)
                self.assertEqual(response.status_code, expected_status)
                self.assertIn(expected_key, response.data)

                if name == "Success":
                    self.assertTrue(
                        User.objects.filter(email=payload["email"]).exists()
                    )
                    mock_trigger.assert_called_once()


class GoogleLoginViewTestCase(APITestBase):
    url = reverse("core:google-login")

    @patch("core.tasks.send_email_notification.delay")
    @patch("core.models.managers.user_managers.id_token.verify_oauth2_token")
    def test_google_login_scenarios(self, mock_verify, mock_send_email):
        self.client.credentials()

        scenarios = [
            (
                "Success New User",
                {"email": "new@gmail.com", "given_name": "New"},
                status.HTTP_200_OK,
                True,
            ),
            (
                "Success Existing User",
                {"email": "existing@gmail.com", "given_name": "Ex"},
                status.HTTP_200_OK,
                False,
            ),
        ]

        UserFactory(email="existing@gmail.com", auth_provider="google")

        for name, mock_data, expected_status, expect_email in scenarios:
            with self.subTest(name=name):
                mock_verify.reset_mock()
                mock_send_email.reset_mock()
                mock_verify.return_value = mock_data

                with self.captureOnCommitCallbacks(execute=True):
                    response = self.client.post(self.url, data={"token": "valid"})

                self.assertEqual(response.status_code, expected_status)
                self.assertIn("access", response.data)

                if expect_email:
                    mock_send_email.assert_called()
                else:
                    mock_send_email.assert_not_called()

    @patch("core.models.managers.user_managers.id_token.verify_oauth2_token")
    def test_google_login_failures(self, mock_verify):
        self.client.credentials()

        mock_verify.side_effect = ValueError("Invalid token")
        response = self.client.post(self.url, data={"token": "bad"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        mock_verify.side_effect = None
        mock_verify.return_value = {"email": "banned@gmail.com"}
        UserFactory(email="banned@gmail.com", is_active=False)

        response = self.client.post(self.url, data={"token": "valid"})
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
