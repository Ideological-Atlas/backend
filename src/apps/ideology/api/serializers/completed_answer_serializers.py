from core.api.serializers import SimpleUserSerializer
from core.helpers import UUIDModelSerializerMixin
from django.utils.translation import gettext_lazy as _
from ideology.models import CompletedAnswer
from rest_framework import serializers


class AxisAnswerInputSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(format="hex")
    value = serializers.IntegerField(required=False, allow_null=True)
    margin_left = serializers.IntegerField(required=False, default=0)
    margin_right = serializers.IntegerField(required=False, default=0)


class ConditionerAnswerInputSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(format="hex")
    value = serializers.CharField()


class CompletedAnswerSerializer(UUIDModelSerializerMixin):
    completed_by = SimpleUserSerializer(read_only=True)

    axis = AxisAnswerInputSerializer(many=True, write_only=True, required=False)
    conditioners = ConditionerAnswerInputSerializer(
        many=True, write_only=True, required=False
    )

    class Meta:
        model = CompletedAnswer
        fields = ["uuid", "created", "answers", "completed_by", "axis", "conditioners"]
        read_only_fields = ["created", "answers", "completed_by", "uuid"]

    def validate(self, attrs):
        user = self.context["request"].user

        if not user.is_authenticated and not {"axis", "conditioners"}.issubset(attrs):
            raise serializers.ValidationError(
                _("Anonymous users must provide 'axis' and 'conditioners' data.")
            )

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        data = None

        if not user.is_authenticated:
            data = {
                "axis": [
                    {**item, "uuid": item["uuid"].hex}
                    for item in validated_data.get("axis", [])
                ],
                "conditioners": [
                    {**item, "uuid": item["uuid"].hex}
                    for item in validated_data.get("conditioners", [])
                ],
            }

        return CompletedAnswer.objects.generate_snapshot(user=user, data=data)
