from typing import Any

from core.factories import CountryFactory, RegionFactory
from django.db.utils import IntegrityError
from django.test import TestCase
from ideology.factories import (
    IdeologyAssociationFactory,
    IdeologyFactory,
    ReligionFactory,
)


class IdeologyAssociationModelTestCase(TestCase):
    def test_string_representation_permutations(self):
        ideology = IdeologyFactory(name="IdeologyUnique")
        religion = ReligionFactory(name="RelUnique")
        country = CountryFactory(name="SpainUnique")
        region = RegionFactory(name="MadridUnique", country=country)

        scenarios: list[tuple[str, dict[str, Any], str]] = [
            (
                "Full Context",
                {
                    "ideology": ideology,
                    "country": country,
                    "religion": religion,
                    "region": region,
                },
                "IdeologyUnique in SpainUnique (MadridUnique) linked to RelUnique",
            ),
            (
                "Only Country",
                {
                    "ideology": ideology,
                    "country": country,
                    "region": None,
                    "religion": None,
                },
                "IdeologyUnique in SpainUnique",
            ),
            (
                "Only Region",
                {
                    "ideology": ideology,
                    "country": None,
                    "region": region,
                    "religion": None,
                },
                "IdeologyUnique (MadridUnique)",
            ),
            (
                "Only Religion",
                {
                    "ideology": ideology,
                    "country": None,
                    "region": None,
                    "religion": religion,
                },
                "IdeologyUnique linked to RelUnique",
            ),
            (
                "Country and Religion",
                {
                    "ideology": ideology,
                    "country": country,
                    "region": None,
                    "religion": religion,
                },
                "IdeologyUnique in SpainUnique linked to RelUnique",
            ),
        ]

        for name, kwargs, expected_string in scenarios:
            with self.subTest(scenario=name):
                ideology_association = IdeologyAssociationFactory.build(**kwargs)
                self.assertEqual(str(ideology_association), expected_string)

    def test_constraint_requires_context(self):
        with self.assertRaises(IntegrityError):
            IdeologyAssociationFactory(country=None, region=None, religion=None)
