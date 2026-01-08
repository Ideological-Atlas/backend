from core.helpers import UUIDModelSerializerMixin
from ideology.models import CompletedAnswer


class CompletedAnswerSerializer(UUIDModelSerializerMixin):
    class Meta:
        model = CompletedAnswer
        fields = ["uuid", "created", "answers"]
        read_only_fields = ["created", "answers"]
