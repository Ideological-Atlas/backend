from django.test import TestCase
from ideology.factories import IdeologyAxisFactory


class IdeologyAxisModelTestCase(TestCase):
    def test_str(self):
        ideology_axis = IdeologyAxisFactory(
            name="Market", left_label="Controlled", right_label="Free"
        )
        self.assertEqual(str(ideology_axis), "Market (Controlled <-> Free)")
