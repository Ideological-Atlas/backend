from django.test import TestCase
from ideology.factories import IdeologyReferenceFactory


class IdeologyReferenceModelTestCase(TestCase):
    def test_create(self):
        ref = IdeologyReferenceFactory(name="Book X")
        self.assertTrue(ref.uuid)
