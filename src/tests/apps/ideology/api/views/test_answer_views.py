import uuid

from core.api.api_test_helpers import APITestBaseNeedAuthorized
from django.urls import reverse
from ideology.factories import (
    IdeologyAbstractionComplexityFactory,
    IdeologyAxisFactory,
    IdeologyConditionerFactory,
    IdeologySectionFactory,
)
from ideology.models import AxisAnswer, ConditionerAnswer, IdeologySectionConditioner
from rest_framework import status


class AxisAnswerViewTestCase(APITestBaseNeedAuthorized):
    def setUp(self):
        super().setUp()
        self.section = IdeologySectionFactory()
        self.axis = IdeologyAxisFactory(section=self.section)
        self.upsert_url = reverse(
            "ideology:upsert-axis-answer", kwargs={"uuid": self.axis.uuid}
        )
        self.list_url = reverse(
            "ideology:user-axis-answers-by-section",
            kwargs={"section_uuid": self.section.uuid},
        )

    def test_upsert_flow_and_list(self):
        steps = [
            ("Create", {"value": 50}, status.HTTP_201_CREATED, 50, 1),
            ("Update", {"value": 90}, status.HTTP_200_OK, 90, 1),
        ]

        for action, data, expected_status, expected_val, expected_count in steps:
            with self.subTest(action=action):
                response = self.client.post(self.upsert_url, data=data)
                self.assertEqual(response.status_code, expected_status)
                self.assertEqual(AxisAnswer.objects.count(), expected_count)
                self.assertEqual(int(response.data["value"]), expected_val)

        with self.subTest(action="List"):
            response = self.client.get(self.list_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 1)

    def test_upsert_axis_not_found(self):
        fake_uuid = uuid.uuid4()
        url = reverse("ideology:upsert-axis-answer", kwargs={"uuid": fake_uuid})
        response = self.client.post(url, data={"value": 0})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ConditionerAnswerViewTestCase(APITestBaseNeedAuthorized):
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
            ("Update", {"answer": "B"}, status.HTTP_200_OK, "B", 1),
        ]

        for action, data, expected_status, expected_val, expected_count in steps:
            with self.subTest(action=action):
                response = self.client.post(self.upsert_url, data=data)
                self.assertEqual(response.status_code, expected_status)
                self.assertEqual(ConditionerAnswer.objects.count(), expected_count)
                self.assertEqual(
                    ConditionerAnswer.objects.get(user=self.user).answer, expected_val
                )

        with self.subTest(action="List"):
            response = self.client.get(self.list_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 1)
