from core.api.api_test_helpers import SerializerTestBase
from ideology.api.serializers import (
    AxisAnswerUpsertSerializer,
    ConditionerAnswerUpsertSerializer,
)


class AnswerSerializersTestCase(SerializerTestBase):
    def test_axis_upsert_validation(self):
        s = AxisAnswerUpsertSerializer(data={"value": 50})
        self.assertTrue(s.is_valid())
        s2 = AxisAnswerUpsertSerializer(data={"value": 150})
        self.assertFalse(s2.is_valid())
        self.assertIn("value", s2.errors)

    def test_conditioner_upsert_validation(self):
        s = ConditionerAnswerUpsertSerializer(data={"answer": "Yes"})
        self.assertTrue(s.is_valid())
        s2 = ConditionerAnswerUpsertSerializer(data={})
        self.assertFalse(s2.is_valid())
        self.assertIn("answer", s2.errors)
