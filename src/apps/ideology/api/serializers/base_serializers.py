from core.helpers import UUIDModelSerializerMixin
from ideology.api.serializers.ideology_conditioner_serializers import (
    IdeologyConditionerSerializer,
)
from rest_framework import serializers


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


class BaseAxisAnswerUpsertSerializer(serializers.Serializer):
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
