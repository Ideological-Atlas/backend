from core.api.api_test_helpers import APITestBaseNeedAuthorized
from core.factories import UserFactory
from django.urls import reverse
from ideology.factories import (
    CompletedAnswerFactory,
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

        self.completed_answer = CompletedAnswerFactory(
            completed_by=self.other_user,
            answers={
                "axis": [
                    {
                        "uuid": self.axis.uuid.hex,
                        "value": 50,
                        "margin_left": 0,
                        "margin_right": 0,
                    }
                ]
            },
        )
        self.url = reverse(
            "core:user-affinity", kwargs={"uuid": self.completed_answer.uuid.hex}
        )

    def test_get_affinity_with_completed_answer(self):
        UserAxisAnswerFactory(user=self.user, axis=self.axis, value=50)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data

        self.assertIn("complexities", data)
        comp_data = data["complexities"][0]
        self.assertEqual(comp_data["complexity"]["name"], "Level 1")

        self.assertEqual(data["total_affinity"], 100.0)
        self.assertEqual(data["target_user"]["uuid"], self.other_user.uuid.hex)

    def test_get_affinity_anonymous_answer(self):
        anon_answer = CompletedAnswerFactory(completed_by=None, answers={"axis": []})
        url = reverse("core:user-affinity", kwargs={"uuid": anon_answer.uuid.hex})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["target_user"])
