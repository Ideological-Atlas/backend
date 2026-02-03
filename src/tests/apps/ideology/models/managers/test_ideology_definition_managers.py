import uuid

from core.exceptions.api_exceptions import NotFoundException
from django.test import TestCase
from ideology.factories import (
    IdeologyAxisFactory,
    IdeologyConditionerFactory,
    IdeologyFactory,
)
from ideology.models import IdeologyAxisDefinition, IdeologyConditionerDefinition


class IdeologyDefinitionManagerTestCase(TestCase):
    def setUp(self):
        self.ideology = IdeologyFactory()
        self.axis = IdeologyAxisFactory()
        self.conditioner = IdeologyConditionerFactory()

    def test_upsert_axis_definition_success(self):
        data = {
            "value": 50,
            "margin_left": 5,
            "margin_right": 5,
            "is_indifferent": False,
        }
        definition, created = IdeologyAxisDefinition.objects.upsert(
            self.ideology.uuid, self.axis.uuid, data
        )
        self.assertTrue(created)
        self.assertEqual(definition.value, 50)

        data["value"] = 80
        definition, created = IdeologyAxisDefinition.objects.upsert(
            self.ideology.uuid, self.axis.uuid, data
        )
        self.assertFalse(created)
        self.assertEqual(definition.value, 80)

    def test_upsert_axis_definition_ideology_not_found(self):
        with self.assertRaises(NotFoundException):
            IdeologyAxisDefinition.objects.upsert(uuid.uuid4(), self.axis.uuid, {})

    def test_upsert_axis_definition_axis_not_found(self):
        with self.assertRaises(NotFoundException):
            IdeologyAxisDefinition.objects.upsert(self.ideology.uuid, uuid.uuid4(), {})

    def test_upsert_conditioner_definition_success(self):
        data = {"answer": "Option A"}
        definition, created = IdeologyConditionerDefinition.objects.upsert(
            self.ideology.uuid, self.conditioner.uuid, data
        )
        self.assertTrue(created)
        self.assertEqual(definition.answer, "Option A")

        data["answer"] = "Option B"
        definition, created = IdeologyConditionerDefinition.objects.upsert(
            self.ideology.uuid, self.conditioner.uuid, data
        )
        self.assertFalse(created)
        self.assertEqual(definition.answer, "Option B")

    def test_upsert_conditioner_definition_ideology_not_found(self):
        with self.assertRaises(NotFoundException):
            IdeologyConditionerDefinition.objects.upsert(
                uuid.uuid4(), self.conditioner.uuid, {}
            )

    def test_upsert_conditioner_definition_conditioner_not_found(self):
        with self.assertRaises(NotFoundException):
            IdeologyConditionerDefinition.objects.upsert(
                self.ideology.uuid, uuid.uuid4(), {}
            )
