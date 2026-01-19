from core.api.api_test_helpers import (
    APITestBase,
    APITestBaseNeedAuthorized,
    SerializerTestBase,
)
from django.test import override_settings
from django.urls import path
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class MockView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response("OK")


urlpatterns = [path("mock/", MockView.as_view(), name="mock")]


@override_settings(ROOT_URLCONF=__name__)
class HelperCoverageTestCase(APITestBaseNeedAuthorized):
    url = "/mock/"

    def test_authorized_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class HelperNoUrlTestCase(APITestBase):
    url = None

    def test_setup_runs_gracefully(self):
        self.assertIsNotNone(self.request)
        self.assertIsNotNone(self.user)


class HelperNeedAuthNoUrlTestCase(APITestBaseNeedAuthorized):
    url = None


class SerializerHelperCoverage(SerializerTestBase):
    def test_setup_run(self):
        self.assertIsNotNone(self.user)
        self.assertIsNotNone(self.request)
