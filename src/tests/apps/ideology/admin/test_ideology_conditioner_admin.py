from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from ideology.admin import IdeologyConditionerAdmin
from ideology.factories import (
    IdeologyConditionerConditionerFactory,
    IdeologyConditionerFactory,
)
from ideology.models import IdeologyConditioner


class IdeologyConditionerAdminTestCase(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = IdeologyConditionerAdmin(IdeologyConditioner, self.site)

    def test_get_condition_count(self):
        target = IdeologyConditionerFactory()
        source = IdeologyConditionerFactory()
        IdeologyConditionerConditionerFactory(
            target_conditioner=target, source_conditioner=source, name="R1"
        )
        self.assertEqual(self.admin.get_condition_count(target), 1)
