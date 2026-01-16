from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from ideology.admin import IdeologyAxisAdmin
from ideology.factories import (
    IdeologyAxisConditionerFactory,
    IdeologyAxisFactory,
    IdeologyConditionerFactory,
)
from ideology.models import IdeologyAxis


class IdeologyAxisAdminTestCase(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = IdeologyAxisAdmin(IdeologyAxis, self.site)

    def test_get_condition_count(self):
        axis = IdeologyAxisFactory()
        cond = IdeologyConditionerFactory()
        IdeologyAxisConditionerFactory(axis=axis, conditioner=cond, name="R1")
        self.assertEqual(self.admin.get_condition_count(axis), 1)
