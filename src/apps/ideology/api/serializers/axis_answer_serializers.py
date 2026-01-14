from core.helpers import UUIDModelSerializerMixin
from ideology.models import IdeologyAxisDefinition, UserAxisAnswer
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

    def create(self, validated_data):
        request = self.context["request"]
        view = self.context["view"]
        axis_uuid = view.kwargs["uuid"]

        answer, _ = UserAxisAnswer.objects.upsert(
            user=request.user, axis_uuid=axis_uuid, validated_data=validated_data
        )
        return answer


class AxisAnswerReadSerializer(UUIDModelSerializerMixin):
    axis_uuid = serializers.UUIDField(source="axis.uuid", format="hex", read_only=True)

    class Meta:
        model = UserAxisAnswer
        fields = [
            "uuid",
            "axis_uuid",
            "value",
            "margin_left",
            "margin_right",
            "is_indifferent",
        ]


class IdeologyAxisDefinitionSerializer(UUIDModelSerializerMixin):
    axis_uuid = serializers.UUIDField(source="axis.uuid", format="hex", read_only=True)

    class Meta:
        model = IdeologyAxisDefinition
        fields = [
            "uuid",
            "axis_uuid",
            "value",
            "margin_left",
            "margin_right",
            "is_indifferent",
        ]
