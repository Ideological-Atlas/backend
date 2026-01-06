from django.test import TestCase
from ideology.factories import IdeologyFactory


class IdeologyModelTestCase(TestCase):
    def test_str(self):
        ideo = IdeologyFactory(name="Lib")
        self.assertEqual(str(ideo), f"{ideo.id}-Lib")
