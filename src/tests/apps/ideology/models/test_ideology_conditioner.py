from django.test import TestCase
from ideology.factories import IdeologyConditionerFactory


class IdeologyConditionerModelTestCase(TestCase):
    def test_str(self):
        cond = IdeologyConditionerFactory(name="Cond1")
        self.assertEqual(str(cond), "Cond1")
