from core.api.api_test_helpers import APITestBase
from django.urls import reverse
from ideology.factories import IdeologyAbstractionComplexityFactory
from rest_framework import status


class AbstractionComplexityViewTestCase(APITestBase):
    url = reverse("ideology:complexity-list")

    def setUp(self):
        self.complexity = IdeologyAbstractionComplexityFactory()
        super().setUp()

    def test_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data["results"]) >= 1)
