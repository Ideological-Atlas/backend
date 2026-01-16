import logging

from core.factories import VerifiedUserFactory
from core.models import User
from django.test.testcases import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class BaseTestCase(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        super().setUp()


class APITestBase(APITestCase):
    url: str | None = None

    def setUp(self) -> None:
        logging.disable(logging.CRITICAL)
        if not self.url:
            self.skipTest("URL must be defined in subclasses.")

        self.user: User = VerifiedUserFactory(password="root1234")  # nosec

        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.request = APIRequestFactory().get(self.url)
        self.request.user = self.user
        self.test_context = {"request": self.request}
        super().setUp()


class APITestBaseNeedAuthorized(APITestBase):
    def test_not_logged_401_unauthorized(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        error_field = response.data.get("message") or response.data.get("detail")
        self.assertEqual(error_field.code, "not_authenticated")


class SerializerTestBase(BaseTestCase):
    def setUp(self) -> None:
        self.user: User = VerifiedUserFactory()
        self.request = APIRequestFactory().post("/foo", data=None)
        self.request.user = self.user
        self.context = {"request": self.request}
        super().setUp()
