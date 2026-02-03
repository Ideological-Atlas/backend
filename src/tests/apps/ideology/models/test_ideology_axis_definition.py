from django.test import TestCase
from ideology.factories import (
    IdeologyAxisDefinitionFactory,
    IdeologyAxisFactory,
    IdeologyFactory,
)


class IdeologyAxisDefinitionModelTestCase(TestCase):
    def setUp(self):
        self.ideology = IdeologyFactory(name="Liberalism")

    def test_axis_definition_str(self):
        ideology_axis = IdeologyAxisFactory(name="Freedom")
        ideology_axis_definition = IdeologyAxisDefinitionFactory(
            ideology=self.ideology, axis=ideology_axis, value=80
        )
        self.assertEqual(str(ideology_axis_definition), "Liberalism - Freedom: 80")
