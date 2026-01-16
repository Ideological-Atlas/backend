from core.helpers import UUIDModelSerializerMixin
from ideology.models import CompletedAnswer


class CompletedAnswerSerializer(UUIDModelSerializerMixin):
    class Meta:
        model = CompletedAnswer
        fields = ["uuid", "created", "answers"]
        read_only_fields = ["created", "answers"]

    def create(self, validated_data):
        request = self.context["request"]
        return CompletedAnswer.objects.generate_snapshot(user=request.user)
