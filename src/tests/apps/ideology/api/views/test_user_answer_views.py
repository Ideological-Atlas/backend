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
        super().setUp()
        self.section = IdeologySectionFactory()
        self.axis = IdeologyAxisFactory(section=self.section)
        self.upsert_url = reverse(
            "ideology:upsert-axis-answer", kwargs={"uuid": self.axis.uuid}
        )
        self.delete_url = reverse(
            "ideology:delete-axis-answer", kwargs={"uuid": self.axis.uuid}
        )
        self.list_url = reverse(
            "ideology:user-axis-answers-by-section",
            kwargs={"section_uuid": self.section.uuid},
        )

    def test_upsert_flow_and_list(self):
        # Test creation
        data_create = {"value": 50, "margin_left": 5, "margin_right": 5}
        response = self.client.post(self.upsert_url, data=data_create, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserAxisAnswer.objects.count(), 1)
        self.assertEqual(response.data["value"], 50)

        # Test update
        data_update = {"value": 90}
        response = self.client.post(self.upsert_url, data=data_update, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserAxisAnswer.objects.count(), 1)
        self.assertEqual(response.data["value"], 90)

        # Test list
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_delete_axis_answer(self):
        UserAxisAnswerFactory(user=self.user, axis=self.axis)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            UserAxisAnswer.objects.filter(user=self.user, axis=self.axis).exists()
        )

    def test_delete_axis_answer_not_found(self):
        # Cubre get_object_or_404 en el delete view
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserConditionerAnswerViewTestCase(APITestBaseNeedAuthorized):
    def setUp(self):
        super().setUp()
        self.complexity = IdeologyAbstractionComplexityFactory()
        self.section = IdeologySectionFactory(abstraction_complexity=self.complexity)
        self.conditioner = IdeologyConditionerFactory()

        IdeologySectionConditioner.objects.create(
            section=self.section,
            conditioner=self.conditioner,
            name="Link",
            condition_values=[],
        )

        self.upsert_url = reverse(
            "ideology:upsert-conditioner-answer", kwargs={"uuid": self.conditioner.uuid}
        )
        self.list_url = reverse(
            "ideology:user-conditioner-answers-by-complexity",
            kwargs={"complexity_uuid": self.complexity.uuid},
        )

    def test_upsert_flow_and_list(self):
        steps = [
            ("Create", {"answer": "A"}, status.HTTP_201_CREATED, "A", 1),
            ("Update", {"answer": "B"}, status.HTTP_201_CREATED, "B", 1),
        ]

        for action, data, expected_status, expected_val, expected_count in steps:
            with self.subTest(action=action):
                response = self.client.post(self.upsert_url, data=data, format="json")
                self.assertEqual(response.status_code, expected_status)
                self.assertEqual(UserConditionerAnswer.objects.count(), expected_count)
                self.assertEqual(
                    UserConditionerAnswer.objects.get(user=self.user).answer,
                    expected_val,
                )

        with self.subTest(action="List"):
            response = self.client.get(self.list_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 1)
