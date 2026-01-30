from core.helpers import UUIDModelSerializerMixin
from ideology.models import IdeologyConditionerDefinition
from rest_framework import serializers


class IdeologyConditionerDefinitionSerializer(UUIDModelSerializerMixin):
    conditioner_uuid = serializers.UUIDField(
        source="conditioner.uuid", format="hex", read_only=True
    )

    class Meta:
        model = IdeologyConditionerDefinition
        fields = ["uuid", "conditioner_uuid", "answer"]


class IdeologyConditionerDefinitionUpsertSerializer(serializers.Serializer):
    answer = serializers.CharField(max_length=255)

    def create(self, validated_data):
        view = self.context["view"]
        ideology_uuid = view.kwargs["ideology_uuid"]
        conditioner_uuid = view.kwargs["conditioner_uuid"]

        definition, _ = IdeologyConditionerDefinition.objects.upsert(
            ideology_uuid=ideology_uuid,
            conditioner_uuid=conditioner_uuid,
            validated_data=validated_data,
        )
        return definition

    def to_representation(self, instance):
        return IdeologyConditionerDefinitionSerializer(
            instance, context=self.context
        ).data
