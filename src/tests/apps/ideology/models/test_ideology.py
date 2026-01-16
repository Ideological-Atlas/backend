from django.test import TestCase
from ideology.factories import IdeologyFactory


class IdeologyModelTestCase(TestCase):
    def test_str(self):
        ideology = IdeologyFactory(name="Liberalism")
        self.assertEqual(str(ideology), f"{ideology.id}-Liberalism")
