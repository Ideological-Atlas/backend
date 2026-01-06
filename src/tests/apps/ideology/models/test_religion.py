from django.test import TestCase
from ideology.factories import ReligionFactory


class ReligionModelTestCase(TestCase):
    def test_str(self):
        rel = ReligionFactory(name="Atheism")
        self.assertEqual(str(rel), "Atheism")
