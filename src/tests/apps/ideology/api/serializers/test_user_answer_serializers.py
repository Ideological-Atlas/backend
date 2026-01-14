from unittest.mock import Mock

from core.api.api_test_helpers import SerializerTestBase
from ideology.api.serializers import (
    AxisAnswerUpsertSerializer,
    ConditionerAnswerUpsertSerializer,
)
from ideology.factories import IdeologyAxisFactory, IdeologyConditionerFactory


class AnswerSerializersTestCase(SerializerTestBase):
    def setUp(self):
        super().setUp()
        self.axis = IdeologyAxisFactory()
        self.conditioner = IdeologyConditionerFactory()

    def test_axis_upsert_create_flow(self):
        view = Mock()
        view.kwargs = {"uuid": self.axis.uuid}
        context = {"request": self.request, "view": view}

        data = {"value": 50, "margin_left": 0, "margin_right": 0}
        serializer = AxisAnswerUpsertSerializer(data=data, context=context)
        self.assertTrue(serializer.is_valid())
        answer = serializer.save()

        self.assertEqual(answer.value, 50)
        self.assertEqual(answer.user, self.user)

    def test_axis_upsert_validation_error(self):
        s2 = AxisAnswerUpsertSerializer(data={"value": 150})
        self.assertFalse(s2.is_valid())
        self.assertIn("value", s2.errors)

    def test_conditioner_upsert_create_flow(self):
        view = Mock()
        view.kwargs = {"uuid": self.conditioner.uuid}
        context = {"request": self.request, "view": view}

        data = {"answer": "Yes"}
        serializer = ConditionerAnswerUpsertSerializer(data=data, context=context)
        self.assertTrue(serializer.is_valid())
        answer = serializer.save()

        self.assertEqual(answer.answer, "Yes")
        self.assertEqual(answer.user, self.user)

    def test_conditioner_upsert_validation_error(self):
        s2 = ConditionerAnswerUpsertSerializer(data={})
        self.assertFalse(s2.is_valid())
        self.assertIn("answer", s2.errors)
