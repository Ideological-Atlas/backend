from core.factories import CountryFactory, RegionFactory
from django.test import TestCase


class GeoModelTestCase(TestCase):
    def test_country_string_representation(self):
        country = CountryFactory(name="Spain")
        self.assertEqual(str(country), "Spain")

    def test_region_string_representation_with_code(self):
        country = CountryFactory(name="Spain", code2="ES")
        region = RegionFactory(name="Madrid", country=country)
        self.assertEqual(str(region), "Madrid (ES)")

    def test_region_string_representation_without_code(self):
        country = CountryFactory(name="Nowhere", code2=None)
        region = RegionFactory(name="HiddenValley", country=country)
        self.assertEqual(str(region), "HiddenValley (N/A)")
