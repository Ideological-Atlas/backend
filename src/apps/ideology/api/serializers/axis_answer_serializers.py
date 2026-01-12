from core.helpers import UUIDModelSerializerMixin
from ideology.models import AxisAnswer
from rest_framework import serializers


class AxisAnswerUpsertSerializer(serializers.Serializer):
    value = serializers.IntegerField(
        min_value=-100,
        max_value=100,
    )


class AxisAnswerReadSerializer(UUIDModelSerializerMixin):
    axis_uuid = serializers.UUIDField(source="axis.uuid", format="hex", read_only=True)

    class Meta:
        model = AxisAnswer
        fields = ["uuid", "axis_uuid", "value"]
