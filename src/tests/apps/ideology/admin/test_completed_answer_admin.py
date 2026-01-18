from unittest.mock import MagicMock

from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from ideology.admin import CompletedAnswerAdmin
from ideology.models import CompletedAnswer


class CompletedAnswerAdminTestCase(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = CompletedAnswerAdmin(CompletedAnswer, self.site)

    def test_answers_pretty_render_json(self):
        obj = MagicMock()
        obj.answers = {"key": "value", "list": [1, 2]}
        result = self.admin.answers_pretty(obj)
        self.assertIn("<pre", result)
        self.assertIn("key", result)
        self.assertIn("value", result)

    def test_answers_pretty_empty_data(self):
        obj = MagicMock()
        obj.answers = {}
        result = self.admin.answers_pretty(obj)
        self.assertEqual(result, "-")

    def test_answers_pretty_none_data(self):
        obj = MagicMock()
        obj.answers = None
        result = self.admin.answers_pretty(obj)
        self.assertEqual(result, "-")
