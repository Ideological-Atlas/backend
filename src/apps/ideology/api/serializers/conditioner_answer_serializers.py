from core.helpers import UUIDModelSerializerMixin
from ideology.models import IdeologyConditionerDefinition, UserConditionerAnswer
from rest_framework import serializers


class ConditionerAnswerUpsertSerializer(serializers.Serializer):
    answer = serializers.CharField(max_length=255)

    def create(self, validated_data):
        request = self.context["request"]
        view = self.context["view"]
        conditioner_uuid = view.kwargs["uuid"]

        answer, _ = UserConditionerAnswer.objects.upsert(
            user=request.user,
            conditioner_uuid=conditioner_uuid,
            validated_data=validated_data,
        )
        return answer


class ConditionerAnswerReadSerializer(UUIDModelSerializerMixin):
    conditioner_uuid = serializers.UUIDField(
        source="conditioner.uuid", format="hex", read_only=True
    )

    class Meta:
        model = UserConditionerAnswer
        fields = [
            "uuid",
            "conditioner_uuid",
            "answer",
        ]


class IdeologyConditionerDefinitionSerializer(UUIDModelSerializerMixin):
    conditioner_uuid = serializers.UUIDField(
        source="conditioner.uuid", format="hex", read_only=True
    )

    class Meta:
        model = IdeologyConditionerDefinition
        fields = ["uuid", "conditioner_uuid", "answer"]
