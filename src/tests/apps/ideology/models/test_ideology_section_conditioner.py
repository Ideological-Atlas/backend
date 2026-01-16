from django.test import TestCase
from ideology.factories import (
    IdeologyConditionerFactory,
    IdeologySectionConditionerFactory,
    IdeologySectionFactory,
)


class IdeologySectionConditionerModelTestCase(TestCase):
    def test_str(self):
        ideology_section = IdeologySectionFactory(name="SectionA")
        ideology_conditioner = IdeologyConditionerFactory()
        ideology_section_conditioner = IdeologySectionConditionerFactory(
            section=ideology_section, conditioner=ideology_conditioner, name="Rule1"
        )
        self.assertEqual(str(ideology_section_conditioner), "SectionA - Rule1")
