from django.test import TestCase
from ideology.factories import IdeologyConditionerFactory
from ideology.models import IdeologyConditionerConditioner


class IdeologyConditionerConditionerModelTestCase(TestCase):
    def test_str(self):
        target = IdeologyConditionerFactory(name="Target")
        source = IdeologyConditionerFactory(name="Source")
        rule = IdeologyConditionerConditioner.objects.create(
            target_conditioner=target, source_conditioner=source, name="RuleX"
        )
        self.assertEqual(str(rule), "Target -> RuleX")
