from django.test import TestCase
from ideology.factories import IdeologyTagFactory


class IdeologyTagModelTestCase(TestCase):
    def test_creation(self):
        link = IdeologyTagFactory()
        self.assertTrue(link.tag)
        self.assertTrue(link.ideology)
