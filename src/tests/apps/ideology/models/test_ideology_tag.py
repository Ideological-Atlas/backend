from django.test import TestCase
from ideology.factories import IdeologyTagFactory


class IdeologyTagModelTestCase(TestCase):
    def test_creation(self):
        ideology_tag_link = IdeologyTagFactory()
        self.assertTrue(ideology_tag_link.tag)
        self.assertTrue(ideology_tag_link.ideology)
