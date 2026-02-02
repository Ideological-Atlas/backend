from core.api.api_test_helpers import APITestBase
from django.urls import reverse
from ideology.factories import TagFactory
from rest_framework import status


class TagListViewTestCase(APITestBase):
    url = reverse("ideology:tag-list")

    def test_list_tags(self):
        TagFactory(name="Test Tag")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Test Tag")

    def test_search_tags(self):
        TagFactory(name="UniqueName")
        TagFactory(name="Other")
        response = self.client.get(self.url, {"search": "Unique"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "UniqueName")
