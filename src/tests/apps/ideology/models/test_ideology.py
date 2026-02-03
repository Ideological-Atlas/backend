from django.test import TestCase
from ideology.factories import (
    IdeologyAxisDefinitionFactory,
    IdeologyAxisFactory,
    IdeologyFactory,
)


class IdeologyModelTestCase(TestCase):
    def test_string_representation(self):
        ideology = IdeologyFactory(name="Liberalism")
        self.assertEqual(str(ideology), f"{ideology.id}-Liberalism")

    def test_get_mapped_for_calculation_defaults_handling(self):
        ideology = IdeologyFactory()
        ideology_axis = IdeologyAxisFactory()

        IdeologyAxisDefinitionFactory(
            ideology=ideology,
            axis=ideology_axis,
            value=50,
            margin_left=None,
            margin_right=None,
            is_indifferent=False,
        )

        mapped_data = ideology.get_mapped_for_calculation()
        axis_data = mapped_data[ideology_axis.uuid.hex]

        self.assertEqual(axis_data["value"], 50)
        self.assertEqual(axis_data["margin_left"], 0)
        self.assertEqual(axis_data["margin_right"], 0)
