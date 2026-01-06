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


class AxisAnswerViewTestCase(APITestBaseNeedAuthorized):
    def setUp(self):
        self.section = IdeologySectionFactory(add_axes__total=0)
        self.axis = IdeologyAxisFactory(section=self.section)

        self.url = reverse(
            "ideology:upsert-axis-answer", kwargs={"uuid": self.axis.uuid}
        )
        self.upsert_url = self.url
        self.list_url = reverse(
            "ideology:user-axis-answers-by-section",
            kwargs={"section_uuid": self.section.uuid},
        )

        super().setUp()

    def test_upsert_flow(self):
        steps = [
            ("Create", {"value": 0.5}, status.HTTP_201_CREATED),
            ("Update", {"value": 0.9}, status.HTTP_200_OK),
        ]

        for action, data, expected_status in steps:
            with self.subTest(action=action):
                response = self.client.post(self.upsert_url, data=data)
                self.assertEqual(response.status_code, expected_status)

    def test_list_answers(self):
        AxisAnswerFactory(user=self.user, axis=self.axis)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_upsert_not_found(self):
        fake_uuid = uuid.uuid4()
        url = reverse("ideology:upsert-axis-answer", kwargs={"uuid": fake_uuid})
        response = self.client.post(url, data={"value": 0})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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
