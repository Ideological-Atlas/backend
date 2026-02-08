from django.test import TestCase
from ideology.services.mapping_helpers import format_mapped_item


class MappingHelpersTestCase(TestCase):
    def test_format_mapped_item_without_item_type(self):
        result = format_mapped_item(
            type="axis",
            value=10,
            complexity_uuid="abc",
        )
        self.assertEqual(result.type, "axis")
        self.assertEqual(result.value, 10)

    def test_format_mapped_item_with_item_type(self):
        result = format_mapped_item(
            item_type="conditioner",
            value="Yes",
            complexity_uuid="abc",
        )
        self.assertEqual(result.type, "conditioner")
        self.assertEqual(result.value, "Yes")
