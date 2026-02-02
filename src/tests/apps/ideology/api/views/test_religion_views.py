from core.api.api_test_helpers import APITestBase
from django.urls import reverse
from ideology.factories import ReligionFactory
from rest_framework import status


class ReligionListViewTestCase(APITestBase):
    url = reverse("ideology:religion-list")

    def test_list_religions(self):
        ReligionFactory(name="Test Religion")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Test Religion")

    def test_search_religions(self):
        ReligionFactory(name="UniqueReligion")
        ReligionFactory(name="Other")
        response = self.client.get(self.url, {"search": "Unique"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "UniqueReligion")
