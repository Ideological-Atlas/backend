from ideology.api.serializers.base_serializers import BaseConditionRuleSerializer
from ideology.models import IdeologyConditionerConditioner
from rest_framework import serializers


class IdeologyConditionerConditionerSerializer(BaseConditionRuleSerializer):

    target_conditioner = serializers.UUIDField(
        source="target_conditioner.uuid", format="hex", read_only=True
    )

    class Meta(BaseConditionRuleSerializer.Meta):
        model = IdeologyConditionerConditioner
        fields = BaseConditionRuleSerializer.Meta.fields + ["target_conditioner"]
