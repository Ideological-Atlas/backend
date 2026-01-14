from core.api.api_test_helpers import APITestBaseNeedAuthorized
from django.urls import reverse
from ideology.factories import (
    IdeologyAxisFactory,
    IdeologyConditionerFactory,
    IdeologySectionFactory,
)
from ideology.models import UserAxisAnswer, UserConditionerAnswer
from rest_framework import status


class UserAxisAnswerViewTestCase(APITestBaseNeedAuthorized):
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

    def test_axis_answer_lifecycle(self):
        cases = [
            (
                "create_standard",
                {"value": 50},
                status.HTTP_201_CREATED,
                50,
                False,
            ),
            (
                "update_value",
                {"value": -25},
                status.HTTP_200_OK,
                -25,
                False,
            ),
            (
                "update_indifferent",
                {"is_indifferent": True},
                status.HTTP_200_OK,
                None,
                True,
            ),
            (
                "revert_to_value",
                {"value": 100, "is_indifferent": False},
                status.HTTP_200_OK,
                100,
                False,
            ),
        ]

        for name, data, expected_status, expected_val, expected_indiff in cases:
            with self.subTest(name=name):
                response = self.client.post(self.upsert_url, data=data)
                self.assertEqual(response.status_code, expected_status)

                answer = UserAxisAnswer.objects.get(user=self.user, axis=self.axis)
                self.assertEqual(answer.is_indifferent, expected_indiff)
                if not expected_indiff:
                    self.assertEqual(answer.value, expected_val)
                else:
                    self.assertIsNone(answer.value)

        with self.subTest(name="list_verification"):
            response = self.client.get(self.list_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 1)
            self.assertEqual(response.data[0]["axis_uuid"], self.axis.uuid.hex)


class UserConditionerAnswerViewTestCase(APITestBaseNeedAuthorized):
    def setUp(self):
        super().setUp()
        self.conditioner = IdeologyConditionerFactory()
        self.upsert_url = reverse(
            "ideology:upsert-conditioner-answer", kwargs={"uuid": self.conditioner.uuid}
        )

    def test_conditioner_answer_lifecycle(self):
        cases = [
            ("create", {"answer": "Option A"}, status.HTTP_201_CREATED, "Option A"),
            ("update", {"answer": "Option B"}, status.HTTP_200_OK, "Option B"),
        ]

        for name, data, expected_status, expected_val in cases:
            with self.subTest(name=name):
                response = self.client.post(self.upsert_url, data=data)
                self.assertEqual(response.status_code, expected_status)

                answer = UserConditionerAnswer.objects.get(
                    user=self.user, conditioner=self.conditioner
                )
                self.assertEqual(answer.answer, expected_val)
