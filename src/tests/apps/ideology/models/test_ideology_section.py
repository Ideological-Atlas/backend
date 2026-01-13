from django.test import TestCase
from ideology.factories import (
    IdeologyAbstractionComplexityFactory,
    IdeologySectionFactory,
)


class IdeologySectionModelTestCase(TestCase):
    def test_str_representations(self):
        abs_comp = IdeologyAbstractionComplexityFactory(name="Basic")

        sec1 = IdeologySectionFactory(name="Eco", abstraction_complexity=abs_comp)
        self.assertEqual(str(sec1), "Eco (Basic)")
