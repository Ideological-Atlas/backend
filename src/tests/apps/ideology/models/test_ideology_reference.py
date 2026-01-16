from django.test import TestCase
from ideology.factories import IdeologyReferenceFactory


class IdeologyReferenceModelTestCase(TestCase):
    def test_create(self):
        ideology_reference = IdeologyReferenceFactory(name="Book X")
        self.assertTrue(ideology_reference.uuid)
