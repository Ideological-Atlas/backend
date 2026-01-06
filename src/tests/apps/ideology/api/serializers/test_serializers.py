from unittest.mock import MagicMock

from core.api.api_test_helpers import SerializerTestBase
from ideology.api.serializers import (
    AxisAnswerUpsertSerializer,
    IdeologySectionSerializer,
)
from ideology.factories import IdeologySectionFactory


class IdeologySerializersTestCase(SerializerTestBase):
    def test_ideology_section_serializer_icon(self):
        section = IdeologySectionFactory()

        cases = [
            ("With Icon", "http://test.com/icon.png", "http://test.com/icon.png"),
            ("Without Icon", None, None),
        ]

        for name, url_value, expected in cases:
            with self.subTest(name=name):
                if url_value:
                    section.icon = MagicMock()
                    section.icon.url = url_value
                else:
                    section.icon = None

                serializer = IdeologySectionSerializer(section)
                self.assertEqual(serializer.data["icon"], expected)

    def test_axis_answer_upsert_validation(self):
        cases = [
            ("Valid", {"axis_uuid": "123", "value": 0.5}, True),
            ("Invalid Range High", {"axis_uuid": "123", "value": 1.5}, False),
            ("Invalid Range Low", {"axis_uuid": "123", "value": -1.5}, False),
        ]

        for name, data, is_valid in cases:
            with self.subTest(name=name):
                serializer = AxisAnswerUpsertSerializer(data=data)
                self.assertEqual(serializer.is_valid(), is_valid)
                if not is_valid:
                    self.assertIn("value", serializer.errors)
