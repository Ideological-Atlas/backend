from core.api.api_test_helpers import APITestBaseNeedAuthorized
from core.factories import UserFactory
from django.urls import reverse
from ideology.factories import (
    CompletedAnswerFactory,
    IdeologyAbstractionComplexityFactory,
    IdeologyAxisDefinitionFactory,
    IdeologyAxisFactory,
    IdeologyFactory,
    IdeologySectionFactory,
    UserAxisAnswerFactory,
)
from rest_framework import status


class MeDetailViewTestCase(APITestBaseNeedAuthorized):
    url = reverse("core:me")

    def test_get_me_detail_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["uuid"], self.user.uuid.hex)
        self.assertIn("auth_provider", response.data)

    def test_patch_me_detail_success(self):
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
        self.ideology_abstraction_complexity = IdeologyAbstractionComplexityFactory(
            name="Level 1"
        )
        self.ideology_section = IdeologySectionFactory(
            name="Econ", abstraction_complexity=self.ideology_abstraction_complexity
        )
        self.ideology_axis = IdeologyAxisFactory(
            name="TestAxis", section=self.ideology_section
        )

        self.completed_answer = CompletedAnswerFactory(
            completed_by=self.other_user,
            answers={
                "axis": [
                    {
                        "uuid": self.ideology_axis.uuid.hex,
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
        UserAxisAnswerFactory(
            user=self.user, axis=self.ideology_axis, value=50, margin_left=0
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data

        self.assertIn("complexities", data)
        complexity_data = data["complexities"][0]
        self.assertEqual(complexity_data["complexity"]["name"], "Level 1")

        self.assertEqual(data["total_affinity"], 100.0)
        self.assertEqual(data["target_user"]["uuid"], self.other_user.uuid.hex)

    def test_get_affinity_anonymous_answer(self):
        anonymous_answer = CompletedAnswerFactory(
            completed_by=None, answers={"axis": []}
        )
        url = reverse("core:user-affinity", kwargs={"uuid": anonymous_answer.uuid.hex})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["target_user"])


class UserIdeologyAffinityViewTestCase(APITestBaseNeedAuthorized):
    def setUp(self):
        super().setUp()
        self.ideology_abstraction_complexity = IdeologyAbstractionComplexityFactory(
            name="Level 1"
        )
        self.ideology_section = IdeologySectionFactory(
            name="Econ", abstraction_complexity=self.ideology_abstraction_complexity
        )
        self.ideology_axis = IdeologyAxisFactory(
            name="TestAxis", section=self.ideology_section
        )

        self.ideology = IdeologyFactory(
            name="TargetIdeology", add_tags__total=0, add_associations__total=0
        )
        IdeologyAxisDefinitionFactory(
            ideology=self.ideology,
            axis=self.ideology_axis,
            value=100,
            margin_left=0,
            margin_right=0,
        )

        self.url = reverse(
            "core:user-ideology-affinity", kwargs={"uuid": self.ideology.uuid.hex}
        )

    def test_get_ideology_affinity_success(self):
        UserAxisAnswerFactory(
            user=self.user, axis=self.ideology_axis, value=100, margin_left=0
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data["target_ideology"]["name"], "TargetIdeology")
        self.assertEqual(data["total_affinity"], 100.0)
        self.assertEqual(len(data["complexities"]), 1)
