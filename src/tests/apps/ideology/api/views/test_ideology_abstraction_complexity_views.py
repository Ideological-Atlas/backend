from core.api.api_test_helpers import APITestBase
from core.factories import UserFactory
from django.urls import reverse
from ideology.factories import IdeologyAbstractionComplexityFactory
from rest_framework import status


class AbstractionComplexityViewTestCase(APITestBase):
    url = reverse("ideology:complexity-list")

    def setUp(self):
        super().setUp()
        self.visible_complexity = IdeologyAbstractionComplexityFactory(visible=True)
        self.hidden_complexity = IdeologyAbstractionComplexityFactory(visible=False)

    def test_list_standard_user_shows_only_visible(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        uuid_list = [r["uuid"] for r in response.data["results"]]
        self.assertIn(self.visible_complexity.uuid.hex, uuid_list)
        self.assertNotIn(self.hidden_complexity.uuid.hex, uuid_list)

    def test_list_staff_user_shows_all(self):
        staff_user = UserFactory(is_staff=True)
        self.client.force_authenticate(user=staff_user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        uuid_list = [r["uuid"] for r in response.data["results"]]
        self.assertIn(self.visible_complexity.uuid.hex, uuid_list)
        self.assertIn(self.hidden_complexity.uuid.hex, uuid_list)
