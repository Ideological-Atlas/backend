from core.api.api_test_helpers import APITestBaseNeedAuthorized
from django.urls import reverse
from ideology.factories import (
    CompletedAnswerFactory,
    IdeologyAbstractionComplexityFactory,
)
from ideology.models import CompletedAnswer
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


class GenerateCompletedAnswerViewTestCase(APITestBaseNeedAuthorized):
    url = reverse("ideology:completed-answer-generate")

    def setUp(self):
        super().setUp()
        IdeologyAbstractionComplexityFactory(complexity=1, name="Basic")

    def test_generate_completed_answer_success(self):
        initial_count = CompletedAnswer.objects.filter(completed_by=self.user).count()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            CompletedAnswer.objects.filter(completed_by=self.user).count(),
            initial_count + 1,
        )
        data = response.data
        self.assertIn("uuid", data)
        self.assertIn("answers", data)
        self.assertIsInstance(data["answers"], list)
