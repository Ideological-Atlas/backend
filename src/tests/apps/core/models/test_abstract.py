import uuid

from core.models.abstract import UUIDModel
from django.test import TestCase


class DummyModel(UUIDModel):
    class Meta:
        app_label = "core"


class DummyNamedModel(UUIDModel):
    name = "TestName"

    class Meta:
        app_label = "core"


class AbstractModelTestCase(TestCase):
    def test_str_representation_standard(self):
        m = DummyModel()
        m.uuid = uuid.uuid4()
        m.id = 1
        self.assertEqual(str(m), f"1-{m.uuid.hex}")

    def test_str_representation_named(self):
        m2 = DummyNamedModel()
        m2.uuid = uuid.uuid4()
        m2.id = 2
        self.assertEqual(str(m2), "2-TestName")

    def test_str_representation_no_id(self):
        m3 = DummyModel()
        m3.uuid = uuid.uuid4()

        if hasattr(m3, "id"):
            del m3.id

        self.assertEqual(str(m3), str(m3.uuid))
