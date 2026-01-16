from django.test import TestCase
from ideology.factories import (
    IdeologyAxisConditionerFactory,
    IdeologyAxisFactory,
    IdeologyConditionerFactory,
)


class IdeologyAxisConditionerModelTestCase(TestCase):
    def test_str(self):
        ideology_axis = IdeologyAxisFactory(name="AxisA")
        ideology_conditioner = IdeologyConditionerFactory()
        ideology_axis_conditioner = IdeologyAxisConditionerFactory(
            axis=ideology_axis, conditioner=ideology_conditioner, name="Rule1"
        )
        self.assertEqual(str(ideology_axis_conditioner), "AxisA - Rule1")
