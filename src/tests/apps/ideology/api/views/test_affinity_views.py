from core.api.api_test_helpers import APITestBase
from core.factories import UserFactory
from django.urls import reverse
from ideology.factories import (
    CompletedAnswerFactory,
    IdeologyAbstractionComplexityFactory,
    IdeologyAxisDefinitionFactory,
    IdeologyAxisFactory,
    IdeologyFactory,
    IdeologySectionFactory,
    UserAxisAnswerFactory,
)
from rest_framework import status


class UserAffinityViewTestCase(APITestBase):
    def setUp(self):
        super().setUp()
        self.other_user = UserFactory()
        self.ideology_abstraction_complexity = IdeologyAbstractionComplexityFactory(
            name="Level 1"
        )
        self.ideology_section = IdeologySectionFactory(
            name="Econ", abstraction_complexity=self.ideology_abstraction_complexity
        )
        self.ideology_axis = IdeologyAxisFactory(
            name="TestAxis", section=self.ideology_section
        )

        self.completed_answer = CompletedAnswerFactory(
            completed_by=self.other_user,
            answers={
                "axis": [
                    {
                        "uuid": self.ideology_axis.uuid.hex,
                        "value": 50,
                        "margin_left": 0,
                        "margin_right": 0,
                    }
                ]
            },
        )
        self.url = reverse(
            "ideology:completed-answer-affinity",
            kwargs={"target_answer_uuid": self.completed_answer.uuid.hex},
        )

    def test_anonymous_request_missing_source_uuid_returns_400(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_source_uuid_valid(self):
        self.client.credentials()
        source_answer = CompletedAnswerFactory(
            completed_by=None,
            answers={
                "axis": [
                    {
                        "uuid": self.ideology_axis.uuid.hex,
                        "value": 50,
                        "margin_left": 0,
                        "margin_right": 0,
                    }
                ]
            },
        )
        response = self.client.get(
            self.url, {"source_answer_uuid": source_answer.uuid.hex}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_affinity"], 100.0)

    def test_with_source_uuid_invalid(self):
        self.client.credentials()
        random_uuid = "00000000000000000000000000000000"
        response = self.client.get(self.url, {"source_answer_uuid": random_uuid})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserIdeologyAffinityViewTestCase(APITestBase):
    def setUp(self):
        super().setUp()
        self.ideology_abstraction_complexity = IdeologyAbstractionComplexityFactory(
            name="Level 1"
        )
        self.ideology_section = IdeologySectionFactory(
            name="Econ", abstraction_complexity=self.ideology_abstraction_complexity
        )
        self.ideology_axis = IdeologyAxisFactory(
            name="TestAxis", section=self.ideology_section
        )

        self.ideology = IdeologyFactory(
            name="TargetIdeology", add_tags__total=0, add_associations__total=0
        )
        IdeologyAxisDefinitionFactory(
            ideology=self.ideology,
            axis=self.ideology_axis,
            value=100,
            margin_left=0,
            margin_right=0,
        )

        self.url = reverse(
            "ideology:ideology-affinity",
            kwargs={"ideology_uuid": self.ideology.uuid.hex},
        )

    def test_anonymous_request_missing_source_uuid_returns_400(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authenticated_user_implicit_source(self):
        UserAxisAnswerFactory(
            user=self.user,
            axis=self.ideology_axis,
            value=100,
            margin_left=0,
            margin_right=0,
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_affinity"], 100.0)
