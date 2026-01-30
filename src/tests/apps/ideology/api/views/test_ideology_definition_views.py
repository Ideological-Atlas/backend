from core.api.api_test_helpers import APITestBase
from core.factories import UserFactory
from django.urls import reverse
from ideology.api.views import (
    IdeologyAxisDefinitionListByIdeologyView,
    IdeologyConditionerDefinitionListByIdeologyView,
)
from ideology.factories import (
    IdeologyAxisDefinitionFactory,
    IdeologyAxisFactory,
    IdeologyConditionerDefinitionFactory,
    IdeologyConditionerFactory,
    IdeologyFactory,
)
from ideology.models import IdeologyAxisDefinition, IdeologyConditionerDefinition
from rest_framework import status


class IdeologyAxisDefinitionViewTestCase(APITestBase):
    def setUp(self):
        super().setUp()
        self.ideology = IdeologyFactory()
        self.axis = IdeologyAxisFactory()
        self.admin_user = UserFactory(is_staff=True)

        self.list_url = reverse(
            "ideology:ideology-axis-definitions-list",
            kwargs={"ideology_uuid": self.ideology.uuid.hex},
        )
        self.upsert_url = reverse(
            "ideology:upsert-ideology-axis-definition",
            kwargs={
                "ideology_uuid": self.ideology.uuid.hex,
                "axis_uuid": self.axis.uuid.hex,
            },
        )

    def test_list_axis_definitions(self):
        IdeologyAxisDefinitionFactory(ideology=self.ideology, axis=self.axis)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_upsert_axis_definition_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {"value": 50, "margin_left": 0, "margin_right": 0}
        response = self.client.post(self.upsert_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(IdeologyAxisDefinition.objects.count(), 1)

    def test_upsert_axis_definition_as_normal_user_forbidden(self):
        # self.user es un usuario normal verificado (definido en APITestBase)
        data = {"value": 50}
        response = self.client.post(self.upsert_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_swagger_fake_view_queryset(self):
        view = IdeologyAxisDefinitionListByIdeologyView()
        view.swagger_fake_view = True
        view.kwargs = {}
        self.assertEqual(view.get_queryset().count(), 0)


class IdeologyConditionerDefinitionViewTestCase(APITestBase):
    def setUp(self):
        super().setUp()
        self.ideology = IdeologyFactory()
        self.conditioner = IdeologyConditionerFactory()
        self.admin_user = UserFactory(is_staff=True)

        self.list_url = reverse(
            "ideology:ideology-conditioner-definitions-list",
            kwargs={"ideology_uuid": self.ideology.uuid.hex},
        )
        self.upsert_url = reverse(
            "ideology:upsert-ideology-conditioner-definition",
            kwargs={
                "ideology_uuid": self.ideology.uuid.hex,
                "conditioner_uuid": self.conditioner.uuid.hex,
            },
        )

    def test_list_conditioner_definitions(self):
        IdeologyConditionerDefinitionFactory(
            ideology=self.ideology, conditioner=self.conditioner
        )
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_upsert_conditioner_definition_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {"answer": "Option X"}
        response = self.client.post(self.upsert_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(IdeologyConditionerDefinition.objects.count(), 1)

    def test_upsert_conditioner_definition_as_normal_user_forbidden(self):
        data = {"answer": "Option X"}
        response = self.client.post(self.upsert_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_swagger_fake_view_queryset(self):
        view = IdeologyConditionerDefinitionListByIdeologyView()
        view.swagger_fake_view = True
        view.kwargs = {}
        self.assertEqual(view.get_queryset().count(), 0)
