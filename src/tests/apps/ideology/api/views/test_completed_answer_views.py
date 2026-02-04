from core.api.api_test_helpers import APITestBase, APITestBaseNeedAuthorized
from django.urls import reverse
from ideology.factories import (
    CompletedAnswerFactory,
    IdeologyAxisFactory,
    IdeologyConditionerFactory,
    UserAxisAnswerFactory,
)
from ideology.models import UserAxisAnswer, UserConditionerAnswer
from rest_framework import status


class LatestCompletedAnswerViewTestCase(APITestBaseNeedAuthorized):
    url = reverse("ideology:completed-answer-latest")

    def test_get_latest_completed_answer_success(self):
        CompletedAnswerFactory(completed_by=self.user, created="2020-01-01T00:00:00Z")
        new_completed_answer = CompletedAnswerFactory(completed_by=self.user)
        CompletedAnswerFactory()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)
        self.assertEqual(response.data["uuid"], new_completed_answer.uuid.hex)

    def test_get_latest_404_if_none_exists(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GenerateCompletedAnswerViewTestCase(APITestBase):
    url = reverse("ideology:completed-answer-generate")

    def test_generate_authenticated_from_db(self):
        axis = IdeologyAxisFactory()
        UserAxisAnswerFactory(user=self.user, axis=axis, value=10)

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.data
        self.assertEqual(data["completed_by"]["uuid"], self.user.uuid.hex)
        self.assertEqual(len(data["answers"]["axis"]), 1)
        self.assertEqual(data["answers"]["axis"][0]["uuid"], axis.uuid.hex)

    def test_generate_anonymous_from_payload(self):
        self.client.credentials()

        payload = {
            "axis": [
                {
                    "uuid": "00000000000000000000000000000001",
                    "value": 50,
                    "margin_left": 0,
                    "margin_right": 0,
                }
            ],
            "conditioners": [
                {"uuid": "00000000000000000000000000000002", "value": "Yes"}
            ],
        }

        response = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.data
        self.assertIsNone(data["completed_by"])
        self.assertEqual(data["answers"], payload)

    def test_generate_anonymous_invalid_payload(self):
        self.client.credentials()
        payload = {"foo": "bar"}
        response = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RetrieveCompletedAnswerViewTestCase(APITestBase):
    def test_retrieve_existing_answer(self):
        completed_answer = CompletedAnswerFactory()
        url = reverse(
            "ideology:completed-answer-detail",
            kwargs={"uuid": completed_answer.uuid.hex},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["uuid"], completed_answer.uuid.hex)

    def test_retrieve_not_found(self):
        url = reverse(
            "ideology:completed-answer-detail",
            kwargs={"uuid": "00000000000000000000000000000000"},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CopyCompletedAnswerViewTestCase(APITestBaseNeedAuthorized):
    def setUp(self):
        super().setUp()
        self.axis = IdeologyAxisFactory()
        self.conditioner = IdeologyConditionerFactory()
        self.completed_answer = CompletedAnswerFactory(
            answers={
                "axis": [
                    {
                        "uuid": self.axis.uuid.hex,
                        "value": 75,
                        "margin_left": 5,
                        "margin_right": 5,
                        "is_indifferent": False,
                    }
                ],
                "conditioners": [{"uuid": self.conditioner.uuid.hex, "value": "Yes"}],
            }
        )
        self.url = reverse(
            "ideology:completed-answer-copy",
            kwargs={"uuid": self.completed_answer.uuid.hex},
        )

    def test_copy_completed_answer_to_profile(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify axis answer copied
        axis_ans = UserAxisAnswer.objects.get(user=self.user, axis=self.axis)
        self.assertEqual(axis_ans.value, 75)
        self.assertEqual(axis_ans.margin_left, 5)

        # Verify conditioner answer copied
        cond_ans = UserConditionerAnswer.objects.get(
            user=self.user, conditioner=self.conditioner
        )
        self.assertEqual(cond_ans.answer, "Yes")
