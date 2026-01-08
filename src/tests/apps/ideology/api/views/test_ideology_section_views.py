from core.api.api_test_helpers import APITestBase
from django.urls import reverse
from ideology.api.views import SectionListByComplexityView
from ideology.factories import (
    IdeologyAbstractionComplexityFactory,
    IdeologySectionFactory,
)
from rest_framework import status


class IdeologySectionViewTestCase(APITestBase):
    def setUp(self):
        self.complexity = IdeologyAbstractionComplexityFactory(add_sections__total=0)
        self.section = IdeologySectionFactory(abstraction_complexity=self.complexity)
        self.url = reverse(
            "ideology:section-list-by-complexity",
            kwargs={"complexity_uuid": self.complexity.uuid},
        )
        super().setUp()

    def test_list_by_complexity(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["uuid"], self.section.uuid.hex)

    def test_get_queryset_direct(self):
        view = SectionListByComplexityView()
        view.kwargs = {"complexity_uuid": self.complexity.uuid}
        qs = view.get_queryset()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), self.section)

    def test_swagger_fake_view_queryset(self):
        view = SectionListByComplexityView()
        view.swagger_fake_view = True
        view.kwargs = {}
        self.assertEqual(view.get_queryset().count(), 0)
