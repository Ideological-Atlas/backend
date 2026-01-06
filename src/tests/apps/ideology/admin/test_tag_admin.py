from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from ideology.admin import TagAdmin
from ideology.factories import IdeologyTagFactory
from ideology.models import Tag


class TagAdminTestCase(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = TagAdmin(Tag, self.site)

    def test_usage_count(self):
        link = IdeologyTagFactory()
        IdeologyTagFactory(tag=link.tag)
        self.assertEqual(self.admin.usage_count(link.tag), 2)
