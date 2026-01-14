from core.helpers import UUIDModelSerializerMixin
from ideology.models import AxisAnswer
from rest_framework import serializers


class AxisAnswerUpsertSerializer(serializers.Serializer):
    value = serializers.IntegerField(
        min_value=-100, max_value=100, required=False, allow_null=True
    )
    margin_left = serializers.IntegerField(
        min_value=0, max_value=200, required=False, allow_null=True
    )
    margin_right = serializers.IntegerField(
        min_value=0, max_value=200, required=False, allow_null=True
    )
    is_indifferent = serializers.BooleanField(required=False, default=False)


class AxisAnswerReadSerializer(UUIDModelSerializerMixin):
    axis_uuid = serializers.UUIDField(source="axis.uuid", format="hex", read_only=True)

    class Meta:
        model = AxisAnswer
        fields = [
            "uuid",
            "axis_uuid",
            "value",
            "margin_left",
            "margin_right",
            "is_indifferent",
        ]
