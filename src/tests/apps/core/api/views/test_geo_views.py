from core.api.api_test_helpers import APITestBase
from core.factories.country_factories import CountryFactory
from core.factories.region_factories import RegionFactory
from django.urls import reverse
from rest_framework import status


class CountryListViewTestCase(APITestBase):
    url = reverse("core:country-list")

    def setUp(self):
        super().setUp()
        self.country = CountryFactory(name="Spain")

    def test_list_countries(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)
        self.assertIsInstance(response.data["results"][0]["id"], int)
        self.assertEqual(response.data["results"][0]["name"], "Spain")


class RegionListViewTestCase(APITestBase):
    url = reverse("core:region-list")

    def setUp(self):
        super().setUp()
        self.country_spain = CountryFactory(name="Spain")
        self.country_france = CountryFactory(name="France")

        self.region_madrid = RegionFactory(name="Madrid", country=self.country_spain)
        self.region_paris = RegionFactory(name="Paris", country=self.country_france)

    def test_list_all_regions_no_filter(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertGreaterEqual(len(results), 2)
        names = [r["name"] for r in results]
        self.assertIn("Madrid", names)
        self.assertIn("Paris", names)

    def test_filter_regions_by_country(self):
        response = self.client.get(self.url, {"country_id": self.country_spain.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Madrid")
        self.assertEqual(results[0]["country"], self.country_spain.id)
