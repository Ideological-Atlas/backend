from core.helpers import UUIDModelSerializerMixin
from ideology.api.serializers.ideology_conditioner_serializers import (
    IdeologyConditionerSerializer,
)
from ideology.models import IdeologySection, IdeologySectionConditioner
from rest_framework import serializers


class IdeologySectionConditionerSerializer(UUIDModelSerializerMixin):
    conditioner = IdeologyConditionerSerializer(read_only=True)

    class Meta:
        model = IdeologySectionConditioner
        fields = ["uuid", "name", "description", "condition_values", "conditioner"]


class IdeologySectionSerializer(UUIDModelSerializerMixin):
    icon = serializers.SerializerMethodField()
    condition_rules = IdeologySectionConditionerSerializer(many=True, read_only=True)

    class Meta:
        model = IdeologySection
        fields = ["uuid", "name", "description", "icon", "condition_rules"]

    @staticmethod
    def get_icon(obj: IdeologySection) -> str | None:
        if obj.icon:
            return obj.icon.url
        return None
