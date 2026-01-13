from django.test import TestCase
from ideology.factories import (
    IdeologyAxisFactory,
    IdeologyConditionerFactory,
)
from ideology.models import IdeologyAxisConditioner


class IdeologyAxisConditionerModelTestCase(TestCase):
    def test_str(self):
        axis = IdeologyAxisFactory(name="AxisA")
        conditioner = IdeologyConditionerFactory()
        rule = IdeologyAxisConditioner.objects.create(
            axis=axis, conditioner=conditioner, name="Rule1"
        )
        self.assertEqual(str(rule), "AxisA - Rule1")
