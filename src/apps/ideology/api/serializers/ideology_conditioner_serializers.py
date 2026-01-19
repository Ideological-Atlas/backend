from core.helpers import UUIDModelSerializerMixin
from ideology.models import IdeologyConditioner
from rest_framework import serializers


class IdeologyConditionerSerializer(UUIDModelSerializerMixin):
    source_axis_uuid = serializers.UUIDField(
        source="source_axis.uuid", format="hex", read_only=True, allow_null=True
    )

    condition_rules = serializers.SerializerMethodField()

    class Meta:
        model = IdeologyConditioner
        fields = [
            "uuid",
            "name",
            "description",
            "type",
            "accepted_values",
            "condition_rules",
            "source_axis_uuid",
            "axis_min_value",
            "axis_max_value",
        ]

    def get_condition_rules(self, instance):
        from ideology.api.serializers import IdeologyConditionerConditionerSerializer

        return IdeologyConditionerConditionerSerializer(
            instance.condition_rules.all(), many=True, context=self.context
        ).data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.type == "axis_range":
            data.pop("accepted_values", None)
        return data
