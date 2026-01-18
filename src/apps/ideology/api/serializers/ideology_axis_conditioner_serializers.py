from ideology.api.serializers.base_serializers import BaseConditionRuleSerializer
from ideology.models import IdeologyAxisConditioner


class IdeologyAxisConditionerSerializer(BaseConditionRuleSerializer):
    class Meta(BaseConditionRuleSerializer.Meta):
        model = IdeologyAxisConditioner
        fields = BaseConditionRuleSerializer.Meta.fields
