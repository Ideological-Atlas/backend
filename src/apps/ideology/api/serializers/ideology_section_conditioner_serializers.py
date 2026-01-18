from ideology.api.serializers.base_serializers import BaseConditionRuleSerializer
from ideology.models import IdeologySectionConditioner


class IdeologySectionConditionerSerializer(BaseConditionRuleSerializer):
    class Meta(BaseConditionRuleSerializer.Meta):
        model = IdeologySectionConditioner
        fields = BaseConditionRuleSerializer.Meta.fields
