from core.api.serializers.base_user_serializers import SimpleUserSerializer
from core.helpers import UUIDModelSerializerMixin
from django.db import transaction
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
        return CompletedAnswer.objects.generate_snapshot(
            user=self.context["request"].user, input_data=validated_data
        )


class CopyCompletedAnswerSerializer(serializers.Serializer):
    def create(self, validated_data):
        from ideology.models import UserAxisAnswer, UserConditionerAnswer

        request = self.context["request"]
        user = request.user
        completed_answer = self.context["view"].get_object()
        answers = completed_answer.answers

        with transaction.atomic():
            for axis_data in answers.get("axis", []):
                UserAxisAnswer.objects.upsert(
                    user=user,
                    axis_uuid=axis_data["uuid"],
                    validated_data={
                        "value": axis_data.get("value"),
                        "margin_left": axis_data.get("margin_left"),
                        "margin_right": axis_data.get("margin_right"),
                        "is_indifferent": axis_data.get("is_indifferent", False),
                    },
                )

            for cond_data in answers.get("conditioners", []):
                UserConditionerAnswer.objects.upsert(
                    user=user,
                    conditioner_uuid=cond_data["uuid"],
                    validated_data={"answer": cond_data.get("value")},
                )
        return completed_answer
