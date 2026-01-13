from core.api.api_test_helpers import APITestBase
from django.urls import reverse
from ideology.factories import (
    IdeologyAbstractionComplexityFactory,
    IdeologyAxisFactory,
    IdeologyConditionerFactory,
    IdeologySectionFactory,
)
from ideology.models import IdeologySectionConditioner
from rest_framework import status


class StructureViewsTestCase(APITestBase):
    def setUp(self):
        self.complexity = IdeologyAbstractionComplexityFactory(add_sections__total=0)
        self.section = IdeologySectionFactory(
            abstraction_complexity=self.complexity, add_axes__total=0
        )
        self.axis = IdeologyAxisFactory(section=self.section)
        self.conditioner = IdeologyConditionerFactory()

        IdeologySectionConditioner.objects.create(
            section=self.section,
            conditioner=self.conditioner,
            name="Test",
            condition_values=[],
        )

        super().setUp()

    def test_endpoints_return_200_and_data(self):
        endpoints = [
            (
                "complexity-list",
                reverse("ideology:complexity-list"),
                self.complexity.uuid.hex,
            ),
            (
                "section-list-by-complexity",
                reverse(
                    "ideology:section-list-by-complexity",
                    kwargs={"complexity_uuid": self.complexity.uuid},
                ),
                self.section.uuid.hex,
            ),
            (
                "axis-list-by-section",
                reverse(
                    "ideology:axis-list-by-section",
                    kwargs={"section_uuid": self.section.uuid},
                ),
                self.axis.uuid.hex,
            ),
            (
                "conditioner-list-aggregated-by-complexity",
                reverse(
                    "ideology:conditioner-list-aggregated-by-complexity",
                    kwargs={"complexity_uuid": self.complexity.uuid},
                ),
                self.conditioner.uuid.hex,
            ),
        ]

        for name, url, expected_uuid in endpoints:
            with self.subTest(endpoint=name):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                data = response.data
                if isinstance(data, dict) and "results" in data:
                    data = data["results"]

                self.assertTrue(len(data) >= 1)

                if expected_uuid:
                    found = any(item["uuid"] == expected_uuid for item in data)
                    self.assertTrue(found, f"UUID {expected_uuid} not found in {name}")
