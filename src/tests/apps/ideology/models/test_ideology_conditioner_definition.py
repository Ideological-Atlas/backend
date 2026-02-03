from django.test import TestCase
from ideology.factories import (
    IdeologyConditionerDefinitionFactory,
    IdeologyConditionerFactory,
    IdeologyFactory,
)


class IdeologyConditionerDefinitionModelTestCase(TestCase):
    def setUp(self):
        self.ideology = IdeologyFactory(name="Liberalism")

    def test_conditioner_definition_str(self):
        ideology_conditioner = IdeologyConditionerFactory(name="Market")
        ideology_conditioner_definition = IdeologyConditionerDefinitionFactory(
            ideology=self.ideology, conditioner=ideology_conditioner, answer="Free"
        )
        self.assertEqual(
            str(ideology_conditioner_definition), "Liberalism - Market: Free"
        )
