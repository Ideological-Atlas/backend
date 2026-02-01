from core.helpers import UUIDModelSerializerMixin
from ideology.api.serializers.ideology_section_conditioner_serializers import (
    IdeologySectionConditionerSerializer,
)
from ideology.models import IdeologySection


class IdeologySectionSerializer(UUIDModelSerializerMixin):
    condition_rules = IdeologySectionConditionerSerializer(many=True, read_only=True)

    class Meta:
        model = IdeologySection
        fields = ["uuid", "name", "description", "icon", "condition_rules"]


class SimpleSectionSerializer(UUIDModelSerializerMixin):
    class Meta:
        model = IdeologySection
        fields = ["uuid", "name", "icon"]
