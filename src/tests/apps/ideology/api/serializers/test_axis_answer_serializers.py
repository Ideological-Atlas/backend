from core.api.api_test_helpers import SerializerTestBase
from ideology.api.serializers import AxisAnswerUpsertSerializer


class AxisAnswerSerializerTestCase(SerializerTestBase):
    def test_validation(self):
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
