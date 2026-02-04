from core.helpers import UUIDModelSerializerMixin
from ideology.api.serializers.base_serializers import BaseAxisAnswerUpsertSerializer
from ideology.models import IdeologyAxisDefinition
from rest_framework import serializers


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


class IdeologyAxisDefinitionUpsertSerializer(BaseAxisAnswerUpsertSerializer):
    def create(self, validated_data):
        view = self.context["view"]
        ideology_uuid = view.kwargs["ideology_uuid"]
        axis_uuid = view.kwargs["axis_uuid"]

        definition, _ = IdeologyAxisDefinition.objects.upsert(
            ideology_uuid=ideology_uuid,
            axis_uuid=axis_uuid,
            validated_data=validated_data,
        )
        return definition

    def to_representation(self, instance):
        return IdeologyAxisDefinitionSerializer(instance, context=self.context).data
