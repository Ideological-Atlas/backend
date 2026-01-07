import uuid
from unittest.mock import MagicMock

from core.api.api_test_helpers import APITestBaseNeedAuthorized
from django.urls import reverse
from ideology.api.views import UserAxisAnswerListBySectionView
from ideology.factories import (
    AxisAnswerFactory,
    IdeologyAxisFactory,
    IdeologySectionFactory,
)
from rest_framework import status


class UpsertAxisAnswerViewTestCase(APITestBaseNeedAuthorized):
    def setUp(self):
        self.section = IdeologySectionFactory(add_axes__total=0)
        self.axis = IdeologyAxisFactory(section=self.section)
        self.url = reverse(
            "ideology:upsert-axis-answer", kwargs={"uuid": self.axis.uuid}
        )
        super().setUp()

    def test_upsert_flow_create_and_update(self):
        response = self.client.post(self.url, data={"value": 0.5})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(float(response.data["value"]), 0.5)
        response = self.client.post(self.url, data={"value": 0.9})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data["value"]), 0.9)

    def test_upsert_not_found(self):
        fake_uuid = uuid.uuid4()
        url = reverse("ideology:upsert-axis-answer", kwargs={"uuid": fake_uuid})
        response = self.client.post(url, data={"value": 0})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserAxisAnswerListBySectionViewTestCase(APITestBaseNeedAuthorized):
    def setUp(self):
        self.section = IdeologySectionFactory(add_axes__total=0)
        self.axis = IdeologyAxisFactory(section=self.section)

        self.url = reverse(
            "ideology:user-axis-answers-by-section",
            kwargs={"section_uuid": self.section.uuid},
        )
        super().setUp()

    def test_list_answers(self):
        AxisAnswerFactory(user=self.user, axis=self.axis)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_get_queryset_direct(self):
        answer = AxisAnswerFactory(user=self.user, axis=self.axis)
        view = UserAxisAnswerListBySectionView()
        view.request = MagicMock()
        view.request.user = self.user
        view.kwargs = {"section_uuid": self.section.uuid}

        qs = view.get_queryset()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), answer)

    def test_swagger_fake_view_queryset(self):
        view = UserAxisAnswerListBySectionView()
        view.swagger_fake_view = True
        view.kwargs = {}
        self.assertEqual(view.get_queryset().count(), 0)
