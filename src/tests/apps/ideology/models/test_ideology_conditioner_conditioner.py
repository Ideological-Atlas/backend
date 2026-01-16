from django.test import TestCase
from ideology.factories import (
    IdeologyConditionerConditionerFactory,
    IdeologyConditionerFactory,
)


class IdeologyConditionerConditionerModelTestCase(TestCase):
    def test_str(self):
        target = IdeologyConditionerFactory(name="Target")
        source = IdeologyConditionerFactory(name="Source")
        rule = IdeologyConditionerConditionerFactory(
            target_conditioner=target, source_conditioner=source, name="RuleX"
        )
        self.assertEqual(str(rule), "Target -> RuleX")
