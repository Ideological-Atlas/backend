from core.helpers import UUIDModelSerializerMixin
from ideology.models import CompletedAnswer
from ideology.services import AnswerService


class CompletedAnswerSerializer(UUIDModelSerializerMixin):
    class Meta:
        model = CompletedAnswer
        fields = ["uuid", "created", "answers"]
        read_only_fields = ["created", "answers"]

    def create(self, validated_data):
        request = self.context["request"]
        return AnswerService.generate_snapshot(user=request.user)
