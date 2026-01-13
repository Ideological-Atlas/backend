from core.api.api_test_helpers import SerializerTestBase
from ideology.api.serializers import AxisAnswerUpsertSerializer


class AxisAnswerSerializerTestCase(SerializerTestBase):
    def test_validation(self):
        cases = [
            ("Valid", {"value": 50}, True),
            (
                "Invalid Range High",
                {"value": 150},
                False,
            ),
            (
                "Invalid Range Low",
                {"value": -150},
                False,
            ),
            (
                "Valid With Margins",
                {"value": 50, "margin_left": 10, "margin_right": 10},
                True,
            ),
            (
                "Invalid Margin Logic High",
                {"value": 90, "margin_right": 20},
                False,
            ),
            (
                "Invalid Margin Logic Low",
                {"value": -90, "margin_left": 20},
                False,
            ),
        ]

        for name, data, is_valid in cases:
            with self.subTest(name=name):
                serializer = AxisAnswerUpsertSerializer(data=data)
                self.assertEqual(serializer.is_valid(), is_valid, serializer.errors)
