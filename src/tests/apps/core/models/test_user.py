from core.exceptions.user_exceptions import UserAlreadyVerifiedException
from core.factories import UserFactory
from django.test import TestCase


class UserModelTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_verify_user_flow(self):
        self.assertFalse(self.user.is_verified)
        self.user.verify()
        self.assertTrue(self.user.is_verified)
        with self.assertRaises(UserAlreadyVerifiedException):
            self.user.verify()

    def test_str_representation(self):
        self.assertEqual(str(self.user), self.user.username)
