from unittest.mock import patch

from core.api.api_test_helpers import APITestBase, APITestBaseNeedAuthorized
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
            "password": "ThisIsARealValidPassword",
        }

    @patch("core.tasks.notifications.requests.post")
    def test_post_create_user_201_created(self, mock_post):
        mock_post.return_value.ok = True
        mock_post.return_value.json.return_value = {"status": "queued"}

        self.client.credentials()  # Logout
        initial_count = User.objects.count()
        response = self.client.post(self.url, data=self.sent_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), initial_count + 1)

        mock_post.assert_called_once()

    def test_post_create_user_400_bad_request(self):
        self.client.credentials()

        collision_email = "collision@test.com"
        UserFactory(email=collision_email)

        test_data_list = [
            (collision_email, "ThisIsARealValidPassword", "email", "unique"),
            (
                "foo@foopass.com",
                "foo@foopassword",
                "password",
                "password_too_similar",
            ),
            ("foo@foopass.com", "short", "password", "password_too_short"),
            ("foo@foopass.com", "12345678", "password", "password_too_common"),
            (
                "foo@foopass.com",
                "141535876321858",
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


class MeDetailViewTestCase(APITestBaseNeedAuthorized):
    url = reverse("core:me")

    def test_get_me_detail_200_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["uuid"], self.user.uuid.hex)

    def test_patch_me_detail_200_ok(self):
        data_to_patch = {
            "first_name": "new_first_name",
            "last_name": "new_last_name",
        }
        response = self.client.patch(self.url, data=data_to_patch)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        for key, value in data_to_patch.items():
            self.assertEqual(str(getattr(self.user, key)), value)

    def test_patch_me_readonly_fields_ignored(self):
        original_email = self.user.email
        data_to_patch = {"email": "hacked@email.com"}
        response = self.client.patch(self.url, data=data_to_patch)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, original_email)


class VerifyUserViewTestCase(APITestBase):
    def setUp(self):
        super().setUp()
        self.target_user = UserFactory(is_verified=False)
        self.url = reverse("core:verify_user", kwargs={"uuid": self.target_user.uuid})

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
