from core.api.api_test_helpers import APITestBaseNeedAuthorized
from django.urls import reverse
from rest_framework import status


class MeDetailViewTestCase(APITestBaseNeedAuthorized):
    url = reverse("core:me")

    def test_get_me_detail_200_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["uuid"], self.user.uuid.hex)
        self.assertIn("auth_provider", response.data)

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


class UserSetPasswordViewTestCase(APITestBaseNeedAuthorized):
    url = reverse("core:set-password")

    def test_set_password_success(self):
        new_pass = "NewStrongPass1!"  # nosec
        response = self.client.put(self.url, data={"new_password": new_pass})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_pass))

    def test_set_password_validation_error(self):
        response = self.client.put(self.url, data={"new_password": "123"})  # nosec
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
