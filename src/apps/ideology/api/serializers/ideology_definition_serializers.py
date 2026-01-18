from core.helpers import UUIDModelSerializerMixin
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
