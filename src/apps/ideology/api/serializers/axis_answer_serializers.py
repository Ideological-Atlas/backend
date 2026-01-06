from decimal import Decimal

from core.helpers import UUIDModelSerializerMixin
from ideology.models import AxisAnswer
from rest_framework import serializers


class AxisAnswerUpsertSerializer(serializers.Serializer):
    value = serializers.DecimalField(
        max_digits=6,
        decimal_places=4,
        min_value=Decimal("-1.0"),
        max_value=Decimal("1.0"),
    )


class AxisAnswerReadSerializer(UUIDModelSerializerMixin):
    axis_uuid = serializers.CharField(source="axis.uuid", read_only=True)

    class Meta:
        model = AxisAnswer
        fields = ["uuid", "axis_uuid", "value"]
