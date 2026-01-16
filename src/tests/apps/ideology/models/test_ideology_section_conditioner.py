from django.test import TestCase
from ideology.factories import (
    IdeologyConditionerFactory,
    IdeologySectionConditionerFactory,
    IdeologySectionFactory,
)


class IdeologySectionConditionerModelTestCase(TestCase):
    def test_str(self):
        section = IdeologySectionFactory(name="SectionA")
        conditioner = IdeologyConditionerFactory()
        rule = IdeologySectionConditionerFactory(
            section=section, conditioner=conditioner, name="Rule1"
        )
        self.assertEqual(str(rule), "SectionA - Rule1")
