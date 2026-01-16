from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import translation
from ideology.factories import IdeologyAxisFactory, IdeologyConditionerFactory
from ideology.models import IdeologyConditioner


class IdeologyConditionerModelTestCase(TestCase):
    def test_str(self):
        cond = IdeologyConditionerFactory(name="Cond1")
        self.assertEqual(str(cond), "Cond1")

    def test_boolean_validation_success(self):
        cond = IdeologyConditioner(
            name="ValidBool",
            type=IdeologyConditioner.ConditionerType.BOOLEAN,
            accepted_values=["true", "false"],
        )
        cond.save()
        self.assertTrue(cond.pk)

    def test_boolean_validation_failure_wrong_values(self):
        cond = IdeologyConditioner(
            name="InvalidBool",
            type=IdeologyConditioner.ConditionerType.BOOLEAN,
            accepted_values=["Yes", "No"],
        )
        with self.assertRaises(ValidationError) as cm:
            cond.save()
        self.assertIn("accepted_values", cm.exception.message_dict)

    def test_boolean_validation_failure_empty(self):
        cond = IdeologyConditioner(
            name="EmptyBool",
            type=IdeologyConditioner.ConditionerType.BOOLEAN,
            accepted_values=[],
        )
        with self.assertRaises(ValidationError):
            cond.save()


class IdeologyConditionerAxisRangeTestCase(TestCase):
    def setUp(self):
        self.axis = IdeologyAxisFactory()

    def test_axis_range_success(self):
        cond = IdeologyConditioner(
            name="ValidRange",
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=self.axis,
            axis_min_value=50,
        )
        cond.save()
        self.assertTrue(cond.pk)

    def test_axis_range_missing_source_axis(self):
        cond = IdeologyConditioner(
            name="InvalidRangeNoAxis",
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=None,
            axis_min_value=50,
        )
        with translation.override("en"):
            with self.assertRaises(ValidationError) as cm:
                cond.save()
            self.assertIn("source_axis", cm.exception.message_dict)
            self.assertIn("Required for Axis Range type", str(cm.exception))

    def test_axis_range_missing_values(self):
        cond = IdeologyConditioner(
            name="InvalidRangeNoValues",
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=self.axis,
            axis_min_value=None,
            axis_max_value=None,
        )
        with translation.override("en"):
            with self.assertRaises(ValidationError) as cm:
                cond.save()
            self.assertIn(
                "Must specify at least min or max value for Axis Range",
                str(cm.exception),
            )
