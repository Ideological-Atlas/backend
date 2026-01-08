from django.test import TestCase
from ideology.factories import TagFactory


class TagModelTestCase(TestCase):
    def test_str(self):
        tag = TagFactory(name="MyTag")
        self.assertEqual(tag.name, "MyTag")
