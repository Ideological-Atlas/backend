from django.test import TestCase
from ideology.factories import ReligionFactory


class ReligionModelTestCase(TestCase):
    def test_str(self):
        religion = ReligionFactory(name="Atheism")
        self.assertEqual(str(religion), "Atheism")
