from core.factories import UserFactory
from core.tasks.security import clear_reset_password_token
from django.test import TestCase


class SecurityTasksTestCase(TestCase):
    def test_clear_reset_password_token(self):
        user = UserFactory()
        user.initiate_password_reset()
        user.refresh_from_db()
        self.assertIsNotNone(user.reset_password_uuid)

        clear_reset_password_token(user.id)

        user.refresh_from_db()
        self.assertIsNone(user.reset_password_uuid)

    def test_clear_reset_password_token_user_not_found(self):
        clear_reset_password_token(999999)

    def test_clear_reset_password_token_noop_if_already_none(self):
        user = UserFactory(reset_password_uuid=None)

        clear_reset_password_token(user.id)

        user.refresh_from_db()
        self.assertIsNone(user.reset_password_uuid)
