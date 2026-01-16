from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import translation
from ideology.factories import IdeologyAxisFactory, IdeologyConditionerFactory
from ideology.models import IdeologyConditioner


class IdeologyConditionerModelTestCase(TestCase):
    def test_str(self):
        ideology_conditioner = IdeologyConditionerFactory(name="Conditioner1")
        self.assertEqual(str(ideology_conditioner), "Conditioner1")

    def test_boolean_validation_success(self):
        ideology_conditioner = IdeologyConditioner(
            name="ValidBooleanConditioner",
            type=IdeologyConditioner.ConditionerType.BOOLEAN,
            accepted_values=["true", "false"],
        )
        ideology_conditioner.save()
        self.assertTrue(ideology_conditioner.pk)

    def test_boolean_validation_failure_wrong_values(self):
        ideology_conditioner = IdeologyConditioner(
            name="InvalidBooleanConditioner",
            type=IdeologyConditioner.ConditionerType.BOOLEAN,
            accepted_values=["Yes", "No"],
        )
        with self.assertRaises(ValidationError) as validation_error:
            ideology_conditioner.save()
        self.assertIn("accepted_values", validation_error.exception.message_dict)

    def test_boolean_validation_failure_empty(self):
        ideology_conditioner = IdeologyConditioner(
            name="EmptyBooleanConditioner",
            type=IdeologyConditioner.ConditionerType.BOOLEAN,
            accepted_values=[],
        )
        with self.assertRaises(ValidationError):
            ideology_conditioner.save()


class IdeologyConditionerAxisRangeTestCase(TestCase):
    def setUp(self):
        self.ideology_axis = IdeologyAxisFactory()

    def test_axis_range_success(self):
        ideology_conditioner = IdeologyConditioner(
            name="ValidRangeConditioner",
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=self.ideology_axis,
            axis_min_value=50,
        )
        ideology_conditioner.save()
        self.assertTrue(ideology_conditioner.pk)

    def test_axis_range_missing_source_axis(self):
        ideology_conditioner = IdeologyConditioner(
            name="InvalidRangeNoAxisConditioner",
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=None,
            axis_min_value=50,
        )
        with translation.override("en"):
            with self.assertRaises(ValidationError) as validation_error:
                ideology_conditioner.save()
            self.assertIn("source_axis", validation_error.exception.message_dict)
            self.assertIn(
                "Required for Axis Range type", str(validation_error.exception)
            )

    def test_axis_range_missing_values(self):
        ideology_conditioner = IdeologyConditioner(
            name="InvalidRangeNoValuesConditioner",
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=self.ideology_axis,
            axis_min_value=None,
            axis_max_value=None,
        )
        with translation.override("en"):
            with self.assertRaises(ValidationError) as validation_error:
                ideology_conditioner.save()
            self.assertIn(
                "Must specify at least min or max value for Axis Range",
                str(validation_error.exception),
            )
