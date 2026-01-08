from core.helpers import UUIDModelSerializerMixin
from ideology.models import ConditionerAnswer
from rest_framework import serializers


class ConditionerAnswerUpsertSerializer(serializers.Serializer):
    answer = serializers.CharField(max_length=255)


class ConditionerAnswerReadSerializer(UUIDModelSerializerMixin):
    conditioner_uuid = serializers.CharField(source="conditioner.uuid", read_only=True)

    class Meta:
        model = ConditionerAnswer
        fields = ["uuid", "conditioner_uuid", "answer"]
