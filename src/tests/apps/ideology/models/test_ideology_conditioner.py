from django.core.exceptions import ValidationError
from django.test import TestCase
from ideology.factories import IdeologyConditionerFactory
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
