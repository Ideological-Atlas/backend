from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import translation
from ideology.factories import IdeologyAxisFactory, IdeologyConditionerFactory
from ideology.models import IdeologyConditioner


class IdeologyConditionerValidationTestCase(TestCase):
    def test_ideology_conditioner_string_representation_returns_name(self):
        conditioner = IdeologyConditionerFactory(name="Conditioner1")
        self.assertEqual(str(conditioner), "Conditioner1")

    def test_clean_method_raises_validation_error_for_invalid_accepted_values_structure(
        self,
    ):
        scenarios = [
            (
                "dict_instead_of_list",
                {"invalid": "dict"},
                "Must be a JSON list",
            ),
            (
                "empty_list_for_categorical",
                [],
                "must define at least one accepted value",
            ),
            (
                "integers_mixed_in_list",
                ["Option A", 123],
                "All values in the list must be strings",
            ),
        ]

        for name, invalid_value, error_message_part in scenarios:
            with self.subTest(scenario=name):
                conditioner = IdeologyConditionerFactory.build(
                    type=IdeologyConditioner.ConditionerType.CATEGORICAL,
                    accepted_values=invalid_value,
                )
                with translation.override("en"):
                    with self.assertRaises(ValidationError) as cm:
                        conditioner.clean()
                    self.assertIn(error_message_part, str(cm.exception))

    def test_clean_method_validates_boolean_logic_strictly(self):
        valid_boolean_conditioner = IdeologyConditionerFactory.build(
            type=IdeologyConditioner.ConditionerType.BOOLEAN,
            accepted_values=["true", "false"],
        )
        try:
            valid_boolean_conditioner.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly for valid boolean")

        invalid_scenarios = [
            ("yes_no_values", ["Yes", "No"]),
            ("partial_values", ["true"]),
            ("empty_values", []),
        ]

        for name, invalid_values in invalid_scenarios:
            with self.subTest(scenario=name):
                conditioner = IdeologyConditionerFactory.build(
                    type=IdeologyConditioner.ConditionerType.BOOLEAN,
                    accepted_values=invalid_values,
                )
                with self.assertRaises(ValidationError) as cm:
                    conditioner.clean()
                self.assertIn("accepted_values", cm.exception.message_dict)


class IdeologyConditionerAxisRangeLogicTestCase(TestCase):
    def setUp(self):
        self.axis = IdeologyAxisFactory()

    def test_clean_method_sets_default_accepted_values_for_axis_range_type(self):
        conditioner = IdeologyConditioner(
            name="ValidRange",
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=self.axis,
            axis_min_value=50,
        )
        conditioner.clean()
        self.assertEqual(conditioner.accepted_values, ["true", "false"])

    def test_clean_method_raises_validation_error_for_incomplete_axis_configuration(
        self,
    ):
        scenarios = [
            (
                "missing_source_axis",
                {"source_axis": None, "axis_min_value": 50},
                "Required for Axis Range type",
            ),
            (
                "missing_min_and_max",
                {
                    "source_axis": self.axis,
                    "axis_min_value": None,
                    "axis_max_value": None,
                },
                "Must specify at least min or max value for Axis Range",
            ),
        ]

        with translation.override("en"):
            for name, kwargs, error_msg in scenarios:
                with self.subTest(scenario=name):
                    conditioner = IdeologyConditionerFactory.build(
                        type=IdeologyConditioner.ConditionerType.AXIS_RANGE, **kwargs
                    )
                    with self.assertRaises(ValidationError) as cm:
                        conditioner.clean()
                    self.assertIn(error_msg, str(cm.exception))
