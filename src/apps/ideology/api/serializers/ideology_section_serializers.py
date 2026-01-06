from core.helpers import UUIDModelSerializerMixin
from ideology.models import IdeologySection
from rest_framework import serializers


class IdeologySectionSerializer(UUIDModelSerializerMixin):
    icon = serializers.SerializerMethodField()

    class Meta:
        model = IdeologySection
        fields = ["uuid", "name", "description", "icon"]

    @staticmethod
    def get_icon(obj: IdeologySection) -> str | None:
        if obj.icon:
            return obj.icon.url
        return None
