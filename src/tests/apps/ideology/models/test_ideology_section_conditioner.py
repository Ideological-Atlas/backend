from django.test import TestCase
from ideology.factories import (
    IdeologyConditionerFactory,
    IdeologySectionFactory,
)
from ideology.models import IdeologySectionConditioner


class IdeologySectionConditionerModelTestCase(TestCase):
    def test_str(self):
        section = IdeologySectionFactory(name="SectionA")
        conditioner = IdeologyConditionerFactory()
        rule = IdeologySectionConditioner.objects.create(
            section=section, conditioner=conditioner, name="Rule1"
        )
        self.assertEqual(str(rule), "SectionA - Rule1")
