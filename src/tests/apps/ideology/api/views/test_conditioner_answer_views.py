from unittest.mock import MagicMock

from core.api.api_test_helpers import APITestBaseNeedAuthorized
from django.urls import reverse
from ideology.api.views import UserConditionerAnswerListByComplexityView
from ideology.factories import (
    ConditionerAnswerFactory,
    IdeologyAbstractionComplexityFactory,
    IdeologyConditionerFactory,
    IdeologySectionFactory,
)
from ideology.models import IdeologySectionConditioner
from rest_framework import status


class UpsertConditionerAnswerViewTestCase(APITestBaseNeedAuthorized):
    def setUp(self):
        self.conditioner = IdeologyConditionerFactory()
        self.url = reverse(
            "ideology:upsert-conditioner-answer", kwargs={"uuid": self.conditioner.uuid}
        )
        super().setUp()

    def test_upsert_flow_create_and_update(self):
        response = self.client.post(self.url, data={"answer": "A"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.url, data={"answer": "B"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserConditionerAnswerListByComplexityViewTestCase(APITestBaseNeedAuthorized):
    def setUp(self):
        self.complexity = IdeologyAbstractionComplexityFactory(add_sections__total=0)
        self.section = IdeologySectionFactory(abstraction_complexity=self.complexity)
        self.conditioner = IdeologyConditionerFactory()

        IdeologySectionConditioner.objects.create(
            section=self.section,
            conditioner=self.conditioner,
            name="Rule",
            condition_values=[],
        )

        self.url = reverse(
            "ideology:user-conditioner-answers-by-complexity",
            kwargs={"complexity_uuid": self.complexity.uuid},
        )
        super().setUp()

    def test_list_answers(self):
        ConditionerAnswerFactory(user=self.user, conditioner=self.conditioner)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_get_queryset_direct(self):
        conditioner_answer = ConditionerAnswerFactory(
            user=self.user, conditioner=self.conditioner
        )
        view = UserConditionerAnswerListByComplexityView()
        view.request = MagicMock()
        view.request.user = self.user
        view.kwargs = {"complexity_uuid": self.complexity.uuid}

        queryset = view.get_queryset()
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), conditioner_answer)

    def test_swagger_fake_view_queryset(self):
        view = UserConditionerAnswerListByComplexityView()
        view.swagger_fake_view = True
        view.kwargs = {}
        self.assertEqual(view.get_queryset().count(), 0)
