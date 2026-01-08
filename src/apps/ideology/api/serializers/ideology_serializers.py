from core.helpers import UUIDModelSerializerMixin
from ideology.api.serializers import (
    AxisAnswerReadSerializer,
    ConditionerAnswerReadSerializer,
)
from ideology.models import Ideology


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

    axis_definitions = AxisAnswerReadSerializer(many=True, read_only=True)
    conditioner_definitions = ConditionerAnswerReadSerializer(many=True, read_only=True)

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
