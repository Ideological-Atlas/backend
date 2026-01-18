from unittest.mock import MagicMock

from core.api.api_test_helpers import SerializerTestBase
from ideology.api.serializers import (
    IdeologySectionConditionerSerializer,
    IdeologySectionSerializer,
)
from ideology.factories import (
    IdeologyAxisFactory,
    IdeologyConditionerFactory,
    IdeologySectionConditionerFactory,
    IdeologySectionFactory,
)
from ideology.models import IdeologyConditioner


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


class IdeologySectionConditionerSerializerTestCase(SerializerTestBase):
    def test_axis_range_conditioner_removes_condition_values(self):
        axis = IdeologyAxisFactory()
        conditioner = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=axis,
            axis_min_value=50,
        )
        rule = IdeologySectionConditionerFactory(conditioner=conditioner)
        serializer = IdeologySectionConditionerSerializer(rule)
        data = serializer.data
        self.assertNotIn("condition_values", data)
        self.assertEqual(data["conditioner"]["type"], "axis_range")

    def test_categorical_conditioner_keeps_condition_values(self):
        conditioner = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.CATEGORICAL,
            accepted_values=["A", "B"],
        )
        rule = IdeologySectionConditionerFactory(
            conditioner=conditioner, condition_values=["A"]
        )
        serializer = IdeologySectionConditionerSerializer(rule)
        data = serializer.data
        self.assertIn("condition_values", data)
        self.assertEqual(data["condition_values"], ["A"])
