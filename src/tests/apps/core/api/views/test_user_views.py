from core.api.api_test_helpers import APITestBaseNeedAuthorized
from core.factories import UserFactory
from django.urls import reverse
from ideology.factories import (
    IdeologyAbstractionComplexityFactory,
    IdeologyAxisFactory,
    IdeologySectionFactory,
    UserAxisAnswerFactory,
)
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
        new_pass = "NewStrongPass1!"
        response = self.client.put(self.url, data={"new_password": new_pass})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_pass))

    def test_set_password_validation_error(self):
        response = self.client.put(self.url, data={"new_password": "123"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserAffinityViewTestCase(APITestBaseNeedAuthorized):
    def setUp(self):
        super().setUp()
        self.other_user = UserFactory()
        self.comp = IdeologyAbstractionComplexityFactory(name="Level 1")
        self.section = IdeologySectionFactory(
            name="Econ", abstraction_complexity=self.comp
        )
        self.axis = IdeologyAxisFactory(name="TestAxis", section=self.section)
        self.url = reverse(
            "core:user-affinity", kwargs={"uuid": self.other_user.uuid.hex}
        )

    def test_get_affinity_full_hierarchy(self):
        UserAxisAnswerFactory(user=self.user, axis=self.axis, value=50)
        UserAxisAnswerFactory(user=self.other_user, axis=self.axis, value=50)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data

        self.assertIn("complexities", data)
        self.assertEqual(len(data["complexities"]), 1)

        comp_data = data["complexities"][0]
        self.assertEqual(comp_data["complexity"]["name"], "Level 1")
        self.assertEqual(comp_data["affinity"], 100.0)

        sec_data = comp_data["sections"][0]
        self.assertEqual(sec_data["section"]["name"], "Econ")
        self.assertEqual(sec_data["affinity"], 100.0)

    def test_get_affinity_user_not_found(self):
        url = reverse(
            "core:user-affinity", kwargs={"uuid": "00000000000000000000000000000000"}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
