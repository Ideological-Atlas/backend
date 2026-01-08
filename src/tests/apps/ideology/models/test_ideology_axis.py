from django.test import TestCase
from ideology.factories import IdeologyAxisFactory


class IdeologyAxisModelTestCase(TestCase):
    def test_str(self):
        axis = IdeologyAxisFactory(name="M", left_label="L", right_label="R")
        self.assertEqual(str(axis), "M (L <-> R)")
