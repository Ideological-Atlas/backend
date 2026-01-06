from django.test import TestCase
from ideology.factories import IdeologyAbstractionComplexityFactory


class IdeologyAbstractionComplexityModelTestCase(TestCase):
    def test_str(self):
        abs_comp = IdeologyAbstractionComplexityFactory(complexity=1, name="Basic")
        self.assertEqual(str(abs_comp), "1 - Basic")
