from django.test import TestCase
from ideology.factories import (
    IdeologyAbstractionComplexityFactory,
    IdeologySectionFactory,
)


class IdeologySectionModelTestCase(TestCase):
    def test_str_representations(self):
        ideology_abstraction_complexity = IdeologyAbstractionComplexityFactory(
            name="Basic"
        )
        ideology_section = IdeologySectionFactory(
            name="Economy", abstraction_complexity=ideology_abstraction_complexity
        )
        self.assertEqual(str(ideology_section), "Economy (Basic)")
