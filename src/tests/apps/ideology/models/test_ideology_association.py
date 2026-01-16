from typing import Any

from django.db.utils import IntegrityError
from django.test import TestCase
from ideology.factories import (
    IdeologyAssociationFactory,
    IdeologyFactory,
    ReligionFactory,
)


class IdeologyAssociationModelTestCase(TestCase):
    def test_str_permutations(self):
        ideology = IdeologyFactory(name="Ideology")
        religion = ReligionFactory(name="Rel")

        scenarios: list[tuple[str, dict[str, Any], list[str], list[str]]] = [
            (
                "Full Context",
                {
                    "ideology": ideology,
                    "country__name": "Spain",
                    "religion": religion,
                    "region": None,
                },
                ["Ideology", "in Spain", "linked to Rel"],
                ["("],
            ),
            (
                "Country Only",
                {
                    "ideology": ideology,
                    "country__name": "Spain",
                    "religion": None,
                    "region": None,
                },
                ["in Spain"],
                ["linked to"],
            ),
            (
                "Religion Only",
                {"ideology": ideology, "trait_religion": True, "religion": religion},
                ["linked to Rel"],
                ["in "],
            ),
            (
                "Region Only",
                {"ideology": ideology, "trait_region": True, "region__name": "Cat"},
                ["(Cat)"],
                ["in "],
            ),
            (
                "No Context (Build Only)",
                {
                    "ideology": ideology,
                    "country": None,
                    "region": None,
                    "religion": None,
                    "factory_method": "build",
                },
                ["Ideology"],
                [],
            ),
        ]

        for name, kwargs, expected_in, expected_not_in in scenarios:
            with self.subTest(scenario=name):
                factory_method = kwargs.pop("factory_method", "create")
                if factory_method == "build":
                    ideology_association = IdeologyAssociationFactory.build(**kwargs)
                else:
                    ideology_association = IdeologyAssociationFactory(**kwargs)

                string_representation = str(ideology_association)

                for substring in expected_in:
                    self.assertIn(substring, string_representation)

                for substring in expected_not_in:
                    self.assertNotIn(substring, string_representation)

    def test_constraint_requires_context(self):
        with self.assertRaises(IntegrityError):
            IdeologyAssociationFactory(country=None, region=None, religion=None)
