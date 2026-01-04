from unittest.mock import MagicMock

from core.api.permissions import IsVerified
from core.factories import UserFactory
from core.helpers import (
    UUIDModelSerializerMixin,
    UUIUpdateView,
    get_admin_image,
    get_admin_path,
    get_admin_reference,
    handle_storage,
)
from core.models import User
from django.test import TestCase
from django.urls import reverse


class HelpersTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_admin_helpers(self):
        expected_url = reverse("admin:core_user_change", args=[self.user.id])
        path = get_admin_path(self.user)
        self.assertEqual(path, expected_url)

        ref = get_admin_reference(self.user)
        self.assertIn(f'href="{expected_url}"', ref)

        obj = MagicMock()
        obj.avatar.url = "http://img.com/a.jpg"
        img_tag = get_admin_image(obj, "avatar")
        self.assertIn('src="http://img.com/a.jpg"', img_tag)

        obj_none = MagicMock()
        obj_none.avatar = None
        self.assertIsNone(get_admin_image(obj_none, "avatar"))

        class Empty:
            pass

        self.assertIsNone(get_admin_image(Empty(), "non_existent"))

    def test_storage_helper(self):
        result = handle_storage(self.user, "photo.jpg")
        self.assertEqual(result, f"User/{self.user.uuid.hex}.jpg")

    def test_permission_helper(self):
        perm = IsVerified()
        req = MagicMock()

        req.user.is_verified = True
        self.assertTrue(perm.has_permission(req, None))

        req.user.is_verified = False
        self.assertFalse(perm.has_permission(req, None))

    def test_serializer_and_view_helpers(self):
        class TestSerializer(UUIDModelSerializerMixin):
            class Meta:
                model = User
                fields = ["uuid"]

        self.assertTrue(TestSerializer().fields["uuid"].read_only)
        self.assertEqual(UUIUpdateView().lookup_field, "uuid")
