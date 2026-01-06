from unittest.mock import MagicMock

from core.api.api_test_helpers import APITestBaseNeedAuthorized
from django.urls import reverse
from ideology.api.views import UserConditionerAnswerListByComplexityView
from ideology.factories import (
    ConditionerAnswerFactory,
    IdeologyAbstractionComplexityFactory,
    IdeologyConditionerFactory,
)
from rest_framework import status


class ConditionerAnswerViewTestCase(APITestBaseNeedAuthorized):
    def setUp(self):
        self.complexity = IdeologyAbstractionComplexityFactory(add_sections__total=0)
        self.conditioner = IdeologyConditionerFactory(
            abstraction_complexity=self.complexity
        )

        self.url = reverse(
            "ideology:upsert-conditioner-answer", kwargs={"uuid": self.conditioner.uuid}
        )
        self.upsert_url = self.url
        self.list_url = reverse(
            "ideology:user-conditioner-answers-by-complexity",
            kwargs={"complexity_uuid": self.complexity.uuid},
        )

        super().setUp()

    def test_upsert_flow(self):
        steps = [
            ("Create", {"answer": "A"}, status.HTTP_201_CREATED),
            ("Update", {"answer": "B"}, status.HTTP_200_OK),
        ]

        for action, data, expected_status in steps:
            with self.subTest(action=action):
                response = self.client.post(self.upsert_url, data=data)
                self.assertEqual(response.status_code, expected_status)

    def test_list_answers(self):
        ConditionerAnswerFactory(user=self.user, conditioner=self.conditioner)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_get_queryset_direct(self):
        answer = ConditionerAnswerFactory(user=self.user, conditioner=self.conditioner)
        view = UserConditionerAnswerListByComplexityView()
        view.request = MagicMock()
        view.request.user = self.user
        view.kwargs = {"complexity_uuid": self.complexity.uuid}

        qs = view.get_queryset()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), answer)

    def test_swagger_fake_view_queryset(self):
        view = UserConditionerAnswerListByComplexityView()
        view.swagger_fake_view = True
        view.kwargs = {}
        self.assertEqual(view.get_queryset().count(), 0)
