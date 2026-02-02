from core.api.api_test_helpers import SerializerTestBase
from ideology.api.serializers import IdeologyDetailSerializer, IdeologyListSerializer
from ideology.factories import (
    IdeologyAssociationFactory,
    IdeologyAxisDefinitionFactory,
    IdeologyConditionerDefinitionFactory,
    IdeologyFactory,
    TagFactory,
)


class IdeologySerializerTestCase(SerializerTestBase):
    def setUp(self):
        super().setUp()
        self.ideology = IdeologyFactory(name="TestIdeology")
        self.tag = TagFactory(name="Tag1")
        self.ideology.tags.add(self.tag)
        self.association = IdeologyAssociationFactory(ideology=self.ideology)

    def test_list_serializer_fields(self):
        serializer = IdeologyListSerializer(self.ideology)
        data = serializer.data
        self.assertIn("uuid", data)
        self.assertIn("name", data)
        self.assertIn("description_supporter", data)
        self.assertIn("tags", data)
        self.assertIn("associated_countries", data)
        self.assertEqual(len(data["tags"]), 1)
        self.assertEqual(len(data["associated_countries"]), 1)
        self.assertNotIn("axis_definitions", data)

    def test_detail_serializer_nested_data(self):
        IdeologyAxisDefinitionFactory(ideology=self.ideology, value=50)
        IdeologyConditionerDefinitionFactory(ideology=self.ideology, answer="Yes")

        serializer = IdeologyDetailSerializer(self.ideology)
        data = serializer.data

        self.assertIn("axis_definitions", data)
        self.assertEqual(len(data["axis_definitions"]), 1)
        self.assertEqual(data["axis_definitions"][0]["value"], 50)

        self.assertIn("conditioner_definitions", data)
        self.assertEqual(len(data["conditioner_definitions"]), 1)
        self.assertEqual(data["conditioner_definitions"][0]["answer"], "Yes")

        self.assertIn("tags", data)
        self.assertEqual(data["tags"][0]["name"], "Tag1")
