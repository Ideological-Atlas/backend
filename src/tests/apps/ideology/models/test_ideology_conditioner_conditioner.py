from django.test import TestCase
from ideology.factories import (
    IdeologyConditionerConditionerFactory,
    IdeologyConditionerFactory,
)


class IdeologyConditionerConditionerModelTestCase(TestCase):
    def test_str(self):
        target_conditioner = IdeologyConditionerFactory(name="Target")
        source_conditioner = IdeologyConditionerFactory(name="Source")
        conditioner_dependency_rule = IdeologyConditionerConditionerFactory(
            target_conditioner=target_conditioner,
            source_conditioner=source_conditioner,
            name="RuleX",
        )
        self.assertEqual(str(conditioner_dependency_rule), "Target -> RuleX")
