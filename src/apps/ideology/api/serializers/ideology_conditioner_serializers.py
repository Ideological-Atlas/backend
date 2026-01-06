from core.helpers import UUIDModelSerializerMixin
from ideology.models import IdeologyConditioner


class IdeologyConditionerSerializer(UUIDModelSerializerMixin):
    class Meta:
        model = IdeologyConditioner
        fields = [
            "uuid",
            "name",
            "description",
            "type",
            "accepted_values",
        ]
