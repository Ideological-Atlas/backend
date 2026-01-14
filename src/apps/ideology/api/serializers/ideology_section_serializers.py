from core.helpers import UUIDModelSerializerMixin
from ideology.api.serializers.ideology_conditioner_serializers import (
    IdeologyConditionerSerializer,
)
from ideology.models import IdeologySection, IdeologySectionConditioner


class IdeologySectionConditionerSerializer(UUIDModelSerializerMixin):
    conditioner = IdeologyConditionerSerializer(read_only=True)

    class Meta:
        model = IdeologySectionConditioner
        fields = ["uuid", "name", "description", "condition_values", "conditioner"]


class IdeologySectionSerializer(UUIDModelSerializerMixin):
    condition_rules = IdeologySectionConditionerSerializer(many=True, read_only=True)

    class Meta:
        model = IdeologySection
        fields = ["uuid", "name", "description", "icon", "condition_rules"]
