from unittest.mock import patch

from core.tasks import send_email_notification
from django.test import TestCase
from requests.exceptions import RequestException


class NotificationsTestCase(TestCase):
    @patch("core.tasks.notifications.requests.post")
    def test_send_email_success(self, mock_post):
        mock_post.return_value.ok = True
        mock_post.return_value.json.return_value = {"ok": True}
        res = send_email_notification(to_email="a@b.com", template_name="t")
        self.assertTrue(res["ok"])

    @patch("core.tasks.notifications.requests.post")
    def test_send_email_retry_logic(self, mock_post):
        mock_post.side_effect = RequestException("Net")
        with self.assertRaises(RequestException):
            send_email_notification(to_email="a@b.com", template_name="t")
        mock_post.side_effect = None
        mock_post.return_value.ok = False
        mock_post.return_value.raise_for_status.side_effect = RequestException("500")
        with self.assertRaises(RequestException):
            send_email_notification(to_email="a@b.com", template_name="t")
