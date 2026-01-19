from core.api.api_test_helpers import SerializerTestBase
from ideology.api.serializers import IdeologyConditionerSerializer
from ideology.factories import IdeologyAxisFactory, IdeologyConditionerFactory
from ideology.models import IdeologyConditioner


class IdeologyConditionerSerializerTestCase(SerializerTestBase):
    def test_axis_range_type_removes_accepted_values(self):
        axis = IdeologyAxisFactory()
        conditioner = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=axis,
            axis_min_value=10,
            accepted_values=["true", "false"],
        )
        serializer = IdeologyConditionerSerializer(conditioner)
        data = serializer.data
        self.assertNotIn("accepted_values", data)
        self.assertEqual(data["type"], "axis_range")

    def test_categorical_type_keeps_accepted_values(self):
        conditioner = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.CATEGORICAL,
            accepted_values=["A", "B"],
        )
        serializer = IdeologyConditionerSerializer(conditioner)
        data = serializer.data
        self.assertIn("accepted_values", data)
        self.assertEqual(data["accepted_values"], ["A", "B"])
