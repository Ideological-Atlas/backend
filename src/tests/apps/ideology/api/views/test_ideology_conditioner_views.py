from core.api.api_test_helpers import APITestBase
from django.urls import reverse
from ideology.api.views import ConditionerListAggregatedByComplexityView
from ideology.factories import (
    IdeologyAbstractionComplexityFactory,
    IdeologyConditionerConditionerFactory,
    IdeologyConditionerFactory,
    IdeologySectionConditionerFactory,
    IdeologySectionFactory,
)
from rest_framework import status


class IdeologyConditionerViewTestCase(APITestBase):
    def setUp(self):
        self.complexity = IdeologyAbstractionComplexityFactory(add_sections__total=0)
        self.section = IdeologySectionFactory(abstraction_complexity=self.complexity)

        self.conditioner_1 = IdeologyConditionerFactory(name="C1")
        IdeologySectionConditionerFactory(
            section=self.section,
            conditioner=self.conditioner_1,
            name="Test Rule",
            condition_values=["A"],
        )

        self.conditioner_2 = IdeologyConditionerFactory(name="C2")
        IdeologyConditionerConditionerFactory(
            target_conditioner=self.conditioner_1,
            source_conditioner=self.conditioner_2,
            name="C1 depends on C2",
            condition_values=["B"],
        )

        self.conditioner_3 = IdeologyConditionerFactory(name="C3")
        IdeologyConditionerConditionerFactory(
            target_conditioner=self.conditioner_2,
            source_conditioner=self.conditioner_3,
            name="C2 depends on C3",
            condition_values=["C"],
        )

        self.conditioner_noise = IdeologyConditionerFactory(name="Noise")

        self.url = reverse(
            "ideology:conditioner-list-aggregated-by-complexity",
            kwargs={"complexity_uuid": self.complexity.uuid},
        )
        super().setUp()

    def test_list_aggregated_by_complexity_includes_recursive_parents(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        uuid_list = [item["uuid"] for item in results]

        self.assertIn(self.conditioner_1.uuid.hex, uuid_list)
        self.assertIn(self.conditioner_2.uuid.hex, uuid_list)
        self.assertIn(self.conditioner_3.uuid.hex, uuid_list)
        self.assertNotIn(self.conditioner_noise.uuid.hex, uuid_list)
        self.assertEqual(len(results), 3)

    def test_get_queryset_direct(self):
        view = ConditionerListAggregatedByComplexityView()
        view.kwargs = {"complexity_uuid": self.complexity.uuid}
        qs = view.get_queryset()
        self.assertTrue(qs.filter(uuid=self.conditioner_1.uuid).exists())
        self.assertTrue(qs.filter(uuid=self.conditioner_3.uuid).exists())

    def test_swagger_fake_view_queryset(self):
        view = ConditionerListAggregatedByComplexityView()
        view.swagger_fake_view = True
        view.kwargs = {}
        view.get_queryset()
