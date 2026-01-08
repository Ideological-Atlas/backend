from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from ideology.admin import IdeologyAdmin
from ideology.factories import IdeologyAssociationFactory, IdeologyFactory
from ideology.models import Ideology


class IdeologyAdminTestCase(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = IdeologyAdmin(Ideology, self.site)

    def test_get_association_count(self):
        ideology = IdeologyFactory(add_associations__total=0)
        IdeologyAssociationFactory(ideology=ideology)
        IdeologyAssociationFactory(ideology=ideology)
        self.assertEqual(self.admin.get_association_count(ideology), 2)
