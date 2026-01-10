from unittest.mock import patch

from core.api.api_test_helpers import APITestBase
from core.factories import UserFactory
from core.models import User
from django.urls import reverse
from rest_framework import status


class RegisterViewTestCase(APITestBase):
    url = reverse("core:register")

    def setUp(self):
        super().setUp()
        self.sent_data = {
            "email": "foo@foo.com",
            "password": "ThisIsARealValidPassword",  # nosec
        }

    @patch("core.tasks.notifications.requests.post")
    def test_post_create_user_201_created(self, mock_post):
        mock_post.return_value.ok = True
        mock_post.return_value.json.return_value = {"status": "queued"}

        self.client.credentials()
        initial_count = User.objects.count()
        response = self.client.post(self.url, data=self.sent_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), initial_count + 1)

        new_user = User.objects.get(email="foo@foo.com")
        self.assertEqual(new_user.auth_provider, User.AuthProvider.INTERNAL)

        mock_post.assert_called_once()

    def test_post_create_user_400_bad_request(self):
        self.client.credentials()

        collision_email = "collision@test.com"
        UserFactory(email=collision_email)

        test_data_list = [
            (collision_email, "ThisIsARealValidPassword", "email", "unique"),  # nosec
            (
                "foo@foopass.com",
                "foo@foopassword",  # nosec
                "password",
                "password_too_similar",
            ),
            ("foo@foopass.com", "short", "password", "password_too_short"),  # nosec
            ("foo@foopass.com", "12345678", "password", "password_too_common"),  # nosec
            (
                "foo@foopass.com",
                "141535876321858",  # nosec
                "password",
                "password_entirely_numeric",
            ),
        ]

        for test_data in test_data_list:
            with self.subTest(test_data=test_data):
                email, password, detail_key, expected_code = test_data
                response = self.client.post(
                    self.url, data={"email": email, "password": password}
                )

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

                error_data = response.data.get(detail_key)
                self.assertIsNotNone(
                    error_data,
                    f"Key '{detail_key}' not found in response: {response.data}",
                )

                if isinstance(error_data, list):
                    code = error_data[0].code
                else:
                    code = error_data.code

                self.assertEqual(code, expected_code)


class GoogleLoginViewTestCase(APITestBase):
    url = reverse("core:google-login")

    @patch("core.models.managers.user_managers.id_token.verify_oauth2_token")
    def test_google_login_success(self, mock_verify):
        self.client.credentials()
        mock_verify.return_value = {
            "email": "g@gmail.com",
            "given_name": "G",
            "family_name": "U",
        }

        response = self.client.post(self.url, data={"token": "valid_google_token"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], "g@gmail.com")
        self.assertEqual(response.data["user"]["auth_provider"], "google")

    @patch("core.models.managers.user_managers.id_token.verify_oauth2_token")
    def test_google_login_invalid_token(self, mock_verify):
        self.client.credentials()
        mock_verify.side_effect = ValueError("Invalid token")

        response = self.client.post(self.url, data={"token": "bad_token"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("core.models.managers.user_managers.id_token.verify_oauth2_token")
    def test_google_login_disabled_user(self, mock_verify):
        self.client.credentials()
        UserFactory(email="disabled@gmail.com", is_active=False)
        mock_verify.return_value = {"email": "disabled@gmail.com"}

        response = self.client.post(self.url, data={"token": "valid_token"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class VerifyUserViewTestCase(APITestBase):
    def setUp(self):
        self.target_user = UserFactory(is_verified=False)
        self.url = reverse("core:verify_user", kwargs={"uuid": self.target_user.uuid})
        super().setUp()

    def test_verify_user_200_ok(self):
        self.client.credentials()
        response = self.client.patch(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.target_user.refresh_from_db()
        self.assertTrue(self.target_user.is_verified)

    def test_verify_user_already_verified_403_forbidden(self):
        self.client.credentials()
        self.target_user.is_verified = True
        self.target_user.save()

        response = self.client.patch(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
