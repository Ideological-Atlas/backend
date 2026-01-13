from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from ideology.admin import IdeologySectionAdmin
from ideology.factories import (
    IdeologyConditionerFactory,
    IdeologySectionFactory,
)
from ideology.models import IdeologySection, IdeologySectionConditioner


class IdeologySectionAdminTestCase(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = IdeologySectionAdmin(IdeologySection, self.site)

    def test_get_condition_count(self):
        section = IdeologySectionFactory()
        cond = IdeologyConditionerFactory()
        IdeologySectionConditioner.objects.create(
            section=section, conditioner=cond, name="R1"
        )
        self.assertEqual(self.admin.get_condition_count(section), 1)
