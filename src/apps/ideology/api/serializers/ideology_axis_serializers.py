from core.helpers import UUIDModelSerializerMixin
from ideology.api.serializers import IdeologyAxisConditionerSerializer
from ideology.models import IdeologyAxis


class IdeologyAxisSerializer(UUIDModelSerializerMixin):
    condition_rules = IdeologyAxisConditionerSerializer(many=True, read_only=True)

    class Meta:
        model = IdeologyAxis
        fields = [
            "uuid",
            "name",
            "description",
            "left_label",
            "right_label",
            "condition_rules",
        ]
