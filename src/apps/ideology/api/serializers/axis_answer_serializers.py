from core.helpers import UUIDModelSerializerMixin
from django.utils.translation import gettext_lazy as _
from ideology.models import AxisAnswer
from rest_framework import serializers


class AxisAnswerUpsertSerializer(serializers.Serializer):
    value = serializers.IntegerField(
        min_value=-100,
        max_value=100,
    )
    margin_left = serializers.IntegerField(
        min_value=-200,
        max_value=200,
        required=False,
    )
    margin_right = serializers.IntegerField(
        min_value=-200,
        max_value=200,
        required=False,
    )

    def validate(self, data):
        value = data.get("value")
        margin_left = data.get("margin_left", 0)
        margin_right = data.get("margin_right", 0)

        if (value - margin_left) < -100:
            raise serializers.ValidationError(
                {
                    "margin_left": _(
                        "Lower bound error: Position minus Left Margin is less than -100"
                    )
                }
            )

        if (value + margin_right) > 100:
            raise serializers.ValidationError(
                {
                    "margin_right": _(
                        "Upper bound error: Position plus Right Margin is greater than 100"
                    )
                }
            )

        return data


class AxisAnswerReadSerializer(UUIDModelSerializerMixin):
    axis_uuid = serializers.UUIDField(source="axis.uuid", format="hex", read_only=True)

    class Meta:
        model = AxisAnswer
        fields = ["uuid", "axis_uuid", "value", "margin_left", "margin_right"]
