from core.helpers import UUIDModelSerializerMixin
from ideology.models import IdeologyConditioner, IdeologyConditionerConditioner
from rest_framework import serializers


class IdeologyConditionerConditionerSerializer(UUIDModelSerializerMixin):
    source_conditioner_uuid = serializers.UUIDField(
        source="source_conditioner.uuid", format="hex", read_only=True
    )

    class Meta:
        model = IdeologyConditionerConditioner
        fields = [
            "uuid",
            "name",
            "description",
            "condition_values",
            "source_conditioner_uuid",
        ]


class IdeologyConditionerSerializer(UUIDModelSerializerMixin):
    condition_rules = IdeologyConditionerConditionerSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = IdeologyConditioner
        fields = [
            "uuid",
            "name",
            "description",
            "type",
            "accepted_values",
            "condition_rules",
        ]
