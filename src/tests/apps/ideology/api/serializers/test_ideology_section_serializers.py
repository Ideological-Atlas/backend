from unittest.mock import MagicMock

from core.api.api_test_helpers import SerializerTestBase
from ideology.api.serializers import IdeologySectionSerializer
from ideology.factories import IdeologySectionFactory


class IdeologySectionSerializerTestCase(SerializerTestBase):
    def test_get_icon(self):
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
