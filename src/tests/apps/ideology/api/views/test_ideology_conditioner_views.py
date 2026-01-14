from core.api.api_test_helpers import APITestBase
from django.urls import reverse
from ideology.api.views import ConditionerListAggregatedByComplexityView
from ideology.factories import (
    IdeologyAbstractionComplexityFactory,
    IdeologyConditionerFactory,
    IdeologySectionFactory,
)
from ideology.models import IdeologySectionConditioner
from rest_framework import status


class IdeologyConditionerViewTestCase(APITestBase):
    def setUp(self):
        self.complexity = IdeologyAbstractionComplexityFactory(add_sections__total=0)
        self.section = IdeologySectionFactory(abstraction_complexity=self.complexity)
        self.conditioner = IdeologyConditionerFactory()
        IdeologySectionConditioner.objects.create(
            section=self.section,
            conditioner=self.conditioner,
            name="Test Rule",
            condition_values=["A"],
        )
        self.url = reverse(
            "ideology:conditioner-list-aggregated-by-complexity",
            kwargs={"complexity_uuid": self.complexity.uuid},
        )
        super().setUp()

    def test_list_aggregated_by_complexity(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        uuid_list = [item["uuid"] for item in response.data["results"]]
        self.assertIn(self.conditioner.uuid.hex, uuid_list)

    def test_get_queryset_direct(self):
        view = ConditionerListAggregatedByComplexityView()
        view.kwargs = {"complexity_uuid": self.complexity.uuid}
        qs = view.get_queryset()
        self.assertTrue(qs.filter(uuid=self.conditioner.uuid).exists())

    def test_swagger_fake_view_queryset(self):
        view = ConditionerListAggregatedByComplexityView()
        view.swagger_fake_view = True
        view.kwargs = {}
        view.get_queryset()
