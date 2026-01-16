from core.api.api_test_helpers import APITestBaseNeedAuthorized
from django.urls import reverse
from ideology.factories import (
    IdeologyAbstractionComplexityFactory,
    IdeologyAxisFactory,
    IdeologyConditionerFactory,
    IdeologySectionFactory,
    UserAxisAnswerFactory,
)
from ideology.models import (
    IdeologySectionConditioner,
    UserAxisAnswer,
    UserConditionerAnswer,
)
from rest_framework import status


class UserAxisAnswerViewTestCase(APITestBaseNeedAuthorized):
    def setUp(self):
        self.section = IdeologySectionFactory()
        self.axis = IdeologyAxisFactory(section=self.section)

        self.url = reverse(
            "ideology:upsert-axis-answer", kwargs={"uuid": self.axis.uuid}
        )

        super().setUp()

        self.delete_url = reverse(
            "ideology:delete-axis-answer", kwargs={"uuid": self.axis.uuid}
        )
        self.list_url = reverse(
            "ideology:user-axis-answers-by-section",
            kwargs={"section_uuid": self.section.uuid},
        )

    def test_upsert_flow(self):
        data = {"value": 50, "margin_left": 5, "margin_right": 5}
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserAxisAnswer.objects.count(), 1)
        self.assertEqual(response.data["value"], 50)

        data_update = {"value": 80}
        response = self.client.post(self.url, data=data_update, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserAxisAnswer.objects.get().value, 80)

    def test_delete_flow(self):
        UserAxisAnswerFactory(user=self.user, axis=self.axis)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(UserAxisAnswer.objects.exists())

    def test_delete_not_found(self):
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_by_section(self):
        UserAxisAnswerFactory(user=self.user, axis=self.axis)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["axis_uuid"], self.axis.uuid.hex)


class UserConditionerAnswerViewTestCase(APITestBaseNeedAuthorized):
    def setUp(self):
        self.complexity = IdeologyAbstractionComplexityFactory()
        self.section = IdeologySectionFactory(abstraction_complexity=self.complexity)
        self.conditioner = IdeologyConditionerFactory()
        IdeologySectionConditioner.objects.create(
            section=self.section, conditioner=self.conditioner, name="rule"
        )

        self.url = reverse(
            "ideology:upsert-conditioner-answer", kwargs={"uuid": self.conditioner.uuid}
        )

        super().setUp()

        self.delete_url = reverse(
            "ideology:delete-conditioner-answer", kwargs={"uuid": self.conditioner.uuid}
        )
        self.list_url = reverse(
            "ideology:user-conditioner-answers-by-complexity",
            kwargs={"complexity_uuid": self.complexity.uuid},
        )

    def test_upsert_flow(self):
        data = {"answer": "Option A"}
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserConditionerAnswer.objects.count(), 1)
        self.assertEqual(response.data["answer"], "Option A")

        data_update = {"answer": "Option B"}
        response = self.client.post(self.url, data=data_update, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserConditionerAnswer.objects.get().answer, "Option B")

    def test_delete_flow(self):
        UserConditionerAnswer.objects.create(
            user=self.user, conditioner=self.conditioner, answer="Val"
        )
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(UserConditionerAnswer.objects.exists())

    def test_delete_not_found(self):
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_by_complexity(self):
        UserConditionerAnswer.objects.create(
            user=self.user, conditioner=self.conditioner, answer="Val"
        )
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["conditioner_uuid"], str(self.conditioner.uuid)
        )
