from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from ideology.admin import IdeologyConditionerAdmin
from ideology.factories import IdeologyConditionerFactory
from ideology.models import IdeologyConditioner, IdeologyConditionerConditioner


class IdeologyConditionerAdminTestCase(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = IdeologyConditionerAdmin(IdeologyConditioner, self.site)

    def test_get_condition_count(self):
        target = IdeologyConditionerFactory()
        source = IdeologyConditionerFactory()
        IdeologyConditionerConditioner.objects.create(
            target_conditioner=target, source_conditioner=source, name="R1"
        )
        self.assertEqual(self.admin.get_condition_count(target), 1)
