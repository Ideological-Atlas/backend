from core.auth_backends import EmailOrUsernameModelBackend
from core.factories import UserFactory
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase


class EmailOrUsernameModelBackendTestCase(TestCase):
    def setUp(self):
        self.backend = EmailOrUsernameModelBackend()
        self.user_password = "secure_password"  # nosec
        self.user = UserFactory(password=self.user_password)
        self.request = RequestFactory().get("/")

    def test_authenticate_standard(self):
        user = self.backend.authenticate(
            self.request, username=self.user.username, password=self.user_password
        )
        self.assertEqual(user, self.user)

        user = self.backend.authenticate(
            self.request, username=self.user.email, password=self.user_password
        )
        self.assertEqual(user, self.user)

    def test_authenticate_kwargs_username(self):
        User = get_user_model()
        kwargs = {User.USERNAME_FIELD: self.user.username}

        user = self.backend.authenticate(
            self.request, password=self.user_password, **kwargs
        )
        self.assertEqual(user, self.user)

    def test_authenticate_missing_username(self):
        user = self.backend.authenticate(
            self.request, username=None, password="password"  # nosec
        )
        self.assertIsNone(user)

    def test_authenticate_failures(self):
        self.assertIsNone(
            self.backend.authenticate(
                self.request, username=self.user.username, password="bad"  # nosec
            )
        )

        self.assertIsNone(
            self.backend.authenticate(
                self.request, username="ghost", password="pwd"  # nosec
            )
        )

        self.user.is_active = False
        self.user.save()
        self.assertIsNone(
            self.backend.authenticate(
                self.request, username=self.user.username, password=self.user_password
            )
        )
