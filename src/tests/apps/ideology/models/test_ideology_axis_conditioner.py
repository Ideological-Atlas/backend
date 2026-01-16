from django.test import TestCase
from ideology.factories import (
    IdeologyAxisConditionerFactory,
    IdeologyAxisFactory,
    IdeologyConditionerFactory,
)


class IdeologyAxisConditionerModelTestCase(TestCase):
    def test_str(self):
        axis = IdeologyAxisFactory(name="AxisA")
        conditioner = IdeologyConditionerFactory()
        rule = IdeologyAxisConditionerFactory(
            axis=axis, conditioner=conditioner, name="Rule1"
        )
        self.assertEqual(str(rule), "AxisA - Rule1")
