from core.helpers import UUIDModelSerializerMixin
from ideology.api.serializers.ideology_conditioner_serializers import (
    IdeologyConditionerSerializer,
)
from ideology.models import IdeologyAxis, IdeologyAxisConditioner


class IdeologyAxisConditionerSerializer(UUIDModelSerializerMixin):
    conditioner = IdeologyConditionerSerializer(read_only=True)

    class Meta:
        model = IdeologyAxisConditioner
        fields = ["uuid", "name", "description", "condition_values", "conditioner"]


class IdeologyAxisSerializer(UUIDModelSerializerMixin):
    condition_rules = IdeologyAxisConditionerSerializer(many=True, read_only=True)

    class Meta:
        model = IdeologyAxis
        fields = [
            "uuid",
            "name",
            "description",
            "left_label",
            "right_label",
            "condition_rules",
        ]
