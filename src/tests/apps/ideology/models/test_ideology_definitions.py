from django.test import TestCase
from ideology.factories import (
    IdeologyAxisDefinitionFactory,
    IdeologyAxisFactory,
    IdeologyConditionerDefinitionFactory,
    IdeologyConditionerFactory,
    IdeologyFactory,
)


class IdeologyDefinitionModelTestCase(TestCase):
    def setUp(self):
        self.ideology = IdeologyFactory(name="Liberalism")

    def test_axis_definition_str(self):
        ideology_axis = IdeologyAxisFactory(name="Freedom")
        ideology_axis_definition = IdeologyAxisDefinitionFactory(
            ideology=self.ideology, axis=ideology_axis, value=80
        )
        self.assertEqual(str(ideology_axis_definition), "Liberalism - Freedom: 80")

    def test_conditioner_definition_str(self):
        ideology_conditioner = IdeologyConditionerFactory(name="Market")
        ideology_conditioner_definition = IdeologyConditionerDefinitionFactory(
            ideology=self.ideology, conditioner=ideology_conditioner, answer="Free"
        )
        self.assertEqual(
            str(ideology_conditioner_definition), "Liberalism - Market: Free"
        )
