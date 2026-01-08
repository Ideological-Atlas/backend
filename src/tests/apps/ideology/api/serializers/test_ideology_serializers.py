from core.api.api_test_helpers import SerializerTestBase
from ideology.api.serializers import IdeologyDetailSerializer, IdeologyListSerializer
from ideology.factories import (
    AxisAnswerFactory,
    ConditionerAnswerFactory,
    IdeologyFactory,
)


class IdeologySerializerTestCase(SerializerTestBase):
    def setUp(self):
        super().setUp()
        self.ideology = IdeologyFactory(name="TestIdeology")

    def test_list_serializer_fields(self):
        serializer = IdeologyListSerializer(self.ideology)
        data = serializer.data
        self.assertIn("uuid", data)
        self.assertIn("name", data)
        self.assertIn("description_supporter", data)
        self.assertNotIn("axis_definitions", data)

    def test_detail_serializer_nested_data(self):
        AxisAnswerFactory(trait_ideology=True, ideology=self.ideology, value=50)
        ConditionerAnswerFactory(
            trait_ideology=True, ideology=self.ideology, answer="Yes"
        )

        serializer = IdeologyDetailSerializer(self.ideology)
        data = serializer.data

        self.assertIn("axis_definitions", data)
        self.assertEqual(len(data["axis_definitions"]), 1)
        self.assertEqual(data["axis_definitions"][0]["value"], 50)

        self.assertIn("conditioner_definitions", data)
        self.assertEqual(len(data["conditioner_definitions"]), 1)
        self.assertEqual(data["conditioner_definitions"][0]["answer"], "Yes")
