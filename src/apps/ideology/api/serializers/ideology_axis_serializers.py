from core.helpers import UUIDModelSerializerMixin
from ideology.models import IdeologyAxis

from .ideology_conditioner_serializers import IdeologyConditionerSerializer


class IdeologyAxisSerializer(UUIDModelSerializerMixin):
    conditioned_by = IdeologyConditionerSerializer(read_only=True)

    class Meta:
        model = IdeologyAxis
        fields = [
            "uuid",
            "name",
            "description",
            "left_label",
            "right_label",
            "conditioned_by",
        ]
