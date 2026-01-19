from core.helpers import UUIDModelSerializerMixin
from ideology.api.serializers.ideology_conditioner_serializers import (
    IdeologyConditionerSerializer,
)


class BaseConditionRuleSerializer(UUIDModelSerializerMixin):
    conditioner = IdeologyConditionerSerializer(read_only=True)

    class Meta:
        abstract = True
        fields = ["uuid", "name", "description", "condition_values", "conditioner"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.conditioner.type == "axis_range":
            data.pop("condition_values", None)
        return data
