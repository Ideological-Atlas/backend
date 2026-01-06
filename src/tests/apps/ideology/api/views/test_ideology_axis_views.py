from core.api.api_test_helpers import APITestBase
from django.urls import reverse
from ideology.api.views import AxisListBySectionView
from ideology.factories import IdeologyAxisFactory, IdeologySectionFactory
from rest_framework import status


class IdeologyAxisViewTestCase(APITestBase):
    def setUp(self):
        self.section = IdeologySectionFactory(add_axes__total=0)
        self.axis = IdeologyAxisFactory(section=self.section)
        self.url = reverse(
            "ideology:axis-list-by-section", kwargs={"section_uuid": self.section.uuid}
        )
        super().setUp()

    def test_list_by_section(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["uuid"], self.axis.uuid.hex)

    def test_get_queryset_direct(self):
        view = AxisListBySectionView()
        view.kwargs = {"section_uuid": self.section.uuid}
        qs = view.get_queryset()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), self.axis)

    def test_swagger_fake_view_queryset(self):
        view = AxisListBySectionView()
        view.swagger_fake_view = True
        view.kwargs = {}
        self.assertEqual(view.get_queryset().count(), 0)
