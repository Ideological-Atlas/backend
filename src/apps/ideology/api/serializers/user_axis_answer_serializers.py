from core.helpers import UUIDModelSerializerMixin
from ideology.api.serializers.base_serializers import BaseAxisAnswerUpsertSerializer
from ideology.models import UserAxisAnswer
from rest_framework import serializers


class UserAxisAnswerReadSerializer(UUIDModelSerializerMixin):
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


class UserAxisAnswerUpsertSerializer(BaseAxisAnswerUpsertSerializer):
    def create(self, validated_data):
        request = self.context["request"]
        view = self.context["view"]
        axis_uuid = view.kwargs["uuid"]

        answer, _ = UserAxisAnswer.objects.upsert(
            user=request.user, axis_uuid=axis_uuid, validated_data=validated_data
        )
        return answer

    def to_representation(self, instance):
        return UserAxisAnswerReadSerializer(instance, context=self.context).data
