from django.core.exceptions import ValidationError
from django.test import TestCase
from ideology.factories import (
    IdeologyConditionerFactory,
    IdeologySectionConditionerFactory,
    IdeologySectionFactory,
)
from ideology.models import IdeologyConditioner


class AbstractConditionRuleValidationTestCase(TestCase):
    def setUp(self):
        self.conditioner = IdeologyConditionerFactory(
            name="ColorConditioner", accepted_values=["Red", "Blue", "Green"]
        )
        self.section = IdeologySectionFactory()

    def test_clean_fails_if_condition_values_is_not_list(self):
        rule = IdeologySectionConditionerFactory.build(
            section=self.section,
            conditioner=self.conditioner,
            condition_values={"bad": "type"},
        )
        with self.assertRaises(ValidationError) as cm:
            rule.clean()
        self.assertIn("Must be a list of values", str(cm.exception))

    def test_clean_fails_if_condition_values_is_empty(self):
        rule = IdeologySectionConditionerFactory.build(
            section=self.section, conditioner=self.conditioner, condition_values=[]
        )
        with self.assertRaises(ValidationError) as cm:
            rule.clean()
        self.assertIn("Trigger values cannot be empty", str(cm.exception))

    def test_clean_fails_if_value_not_in_parent_accepted_values(self):
        rule = IdeologySectionConditionerFactory.build(
            section=self.section,
            conditioner=self.conditioner,
            condition_values=["Red", "Purple"],
        )
        with self.assertRaises(ValidationError) as cm:
            rule.clean()
        self.assertIn("Values ['Purple'] are not valid", str(cm.exception))

    def test_logical_consistency_skipped_if_parent_has_no_values(self):
        free_text_conditioner = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.TEXT, accepted_values=[]
        )
        rule = IdeologySectionConditionerFactory.build(
            section=self.section,
            conditioner=free_text_conditioner,
            condition_values=["Anything goes"],
        )
        try:
            rule.clean()
        except ValidationError:
            self.fail("Validation should be skipped if parent has no accepted_values")
