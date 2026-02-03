from core.api.api_test_helpers import APITestBase
from core.factories.country_factories import CountryFactory
from django.urls import reverse
from ideology.factories import (
    IdeologyAssociationFactory,
    IdeologyAxisDefinitionFactory,
    IdeologyFactory,
    ReligionFactory,
    TagFactory,
)
from rest_framework import status


class IdeologyListViewTestCase(APITestBase):
    url = reverse("ideology:ideology-list")

    def setUp(self):
        super().setUp()
        self.country = CountryFactory()
        self.religion = ReligionFactory()
        self.tag = TagFactory()

        self.target_ideology = IdeologyFactory(
            name="Target Ideology", add_associations__total=0, add_tags__total=0
        )
        self.other_ideology = IdeologyFactory(
            name="Other Ideology", add_associations__total=0, add_tags__total=0
        )

        for ideol in [self.target_ideology, self.other_ideology]:
            for i in range(15):
                IdeologyAxisDefinitionFactory(ideology=ideol)

        IdeologyAssociationFactory(
            ideology=self.target_ideology, country=self.country, religion=self.religion
        )
        self.target_ideology.tags.add(self.tag)

    def test_list_all(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 2)

    def test_filter_by_country(self):
        response = self.client.get(self.url, {"country": self.country.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_by_religion(self):
        response = self.client.get(self.url, {"religion": self.religion.uuid})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_by_tag(self):
        response = self.client.get(self.url, {"tag": self.tag.uuid})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_search_by_name(self):
        response = self.client.get(self.url, {"search": "Target"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
