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
        self.ideology = IdeologyFactory(
            name="TestIdeology", add_tags__total=0, add_associations__total=0
        )
        self.tag = TagFactory(name="Tag1")
        self.ideology.tags.add(self.tag)
        self.ideology_association = IdeologyAssociationFactory(ideology=self.ideology)

    def test_list_serializer_fields(self):
        serializer = IdeologyListSerializer(self.ideology)
        data = serializer.data
        self.assertEqual(len(data["tags"]), 1)
        self.assertEqual(len(data["associated_countries"]), 1)

    def test_detail_serializer_nested_data(self):
        IdeologyAxisDefinitionFactory(ideology=self.ideology, value=50)
        IdeologyConditionerDefinitionFactory(ideology=self.ideology, answer="Yes")
        serializer = IdeologyDetailSerializer(self.ideology)
        data = serializer.data
        tag_names = [tag["name"] for tag in data["tags"]]
        self.assertIn("Tag1", tag_names)
