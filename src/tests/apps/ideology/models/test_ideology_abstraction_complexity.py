from django.test import TestCase
from ideology.factories import IdeologyAbstractionComplexityFactory


class IdeologyAbstractionComplexityModelTestCase(TestCase):
    def test_str(self):
        ideology_abstraction_complexity = IdeologyAbstractionComplexityFactory(
            complexity=1, name="Basic"
        )
        self.assertEqual(str(ideology_abstraction_complexity), "1 - Basic")
