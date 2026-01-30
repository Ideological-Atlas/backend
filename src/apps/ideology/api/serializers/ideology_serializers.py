from core.helpers import UUIDModelSerializerMixin
from ideology.models import Ideology

from .ideology_axis_definition_serializers import IdeologyAxisDefinitionSerializer
from .ideology_conditioner_definition_serializers import (
    IdeologyConditionerDefinitionSerializer,
)


class IdeologyListSerializer(UUIDModelSerializerMixin):
    class Meta:
        model = Ideology
        fields = [
            "uuid",
            "name",
            "description_supporter",
            "description_detractor",
            "description_neutral",
            "flag",
            "background",
            "color",
        ]


class IdeologyDetailSerializer(UUIDModelSerializerMixin):
    axis_definitions = IdeologyAxisDefinitionSerializer(many=True, read_only=True)
    conditioner_definitions = IdeologyConditionerDefinitionSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = Ideology
        fields = [
            "uuid",
            "name",
            "description_supporter",
            "description_detractor",
            "description_neutral",
            "flag",
            "background",
            "color",
            "axis_definitions",
            "conditioner_definitions",
        ]
