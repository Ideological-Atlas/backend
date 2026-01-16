from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import translation
from ideology.factories import IdeologyAxisFactory, IdeologyConditionerFactory
from ideology.models import IdeologyConditioner


class IdeologyConditionerValidationTestCase(TestCase):
    def test_str(self):
        conditioner = IdeologyConditionerFactory(name="Conditioner1")
        self.assertEqual(str(conditioner), "Conditioner1")

    def test_validation_fails_if_accepted_values_is_not_list(self):
        """Coverage for: if not isinstance(self.accepted_values, list)"""
        conditioner = IdeologyConditionerFactory.build(
            accepted_values={"invalid": "dict"}  # Should be a list
        )
        with self.assertRaises(ValidationError) as cm:
            conditioner.clean()
        self.assertIn("Must be a JSON list", str(cm.exception))

    def test_categorical_validation_fails_empty_values(self):
        conditioner = IdeologyConditionerFactory.build(
            type=IdeologyConditioner.ConditionerType.CATEGORICAL, accepted_values=[]
        )
        with self.assertRaises(ValidationError) as cm:
            conditioner.clean()
        self.assertIn("must define at least one accepted value", str(cm.exception))

    def test_categorical_validation_fails_non_string_values(self):
        """Coverage for: if not all(isinstance(x, str) for x in self.accepted_values)"""
        conditioner = IdeologyConditionerFactory.build(
            type=IdeologyConditioner.ConditionerType.CATEGORICAL,
            accepted_values=["Option A", 123],  # Integer is invalid
        )
        with self.assertRaises(ValidationError) as cm:
            conditioner.clean()
        self.assertIn("All values in the list must be strings", str(cm.exception))


class BooleanLogicTestCase(TestCase):
    def test_boolean_validation_success(self):
        conditioner = IdeologyConditionerFactory.build(
            type=IdeologyConditioner.ConditionerType.BOOLEAN,
            accepted_values=["true", "false"],
        )
        # Should not raise
        conditioner.clean()

    def test_boolean_validation_failure_wrong_values(self):
        conditioner = IdeologyConditionerFactory.build(
            type=IdeologyConditioner.ConditionerType.BOOLEAN,
            accepted_values=["Yes", "No"],
        )
        with self.assertRaises(ValidationError) as cm:
            conditioner.clean()
        self.assertIn("accepted_values", cm.exception.message_dict)


class AxisRangeLogicTestCase(TestCase):
    def setUp(self):
        self.axis = IdeologyAxisFactory()

    def test_axis_range_success(self):
        conditioner = IdeologyConditioner(
            name="ValidRange",
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=self.axis,
            axis_min_value=50,
            # accepted_values is auto-set in clean()
        )
        conditioner.clean()
        self.assertEqual(conditioner.accepted_values, ["true", "false"])

    def test_axis_range_missing_source_axis(self):
        """Coverage for: if not self.source_axis: raise ValidationError"""
        conditioner = IdeologyConditionerFactory.build(
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=None,
            axis_min_value=50,
        )
        with translation.override("en"):
            with self.assertRaises(ValidationError) as cm:
                conditioner.clean()
            self.assertIn("Required for Axis Range type", str(cm.exception))

    def test_axis_range_missing_min_max_values(self):
        conditioner = IdeologyConditionerFactory.build(
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=self.axis,
            axis_min_value=None,
            axis_max_value=None,
        )
        with translation.override("en"):
            with self.assertRaises(ValidationError) as cm:
                conditioner.clean()
            self.assertIn(
                "Must specify at least min or max value for Axis Range",
                str(cm.exception),
            )
