from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .ideology_abstraction_complexity_serializers import SimpleComplexitySerializer
from .ideology_axis_serializers import SimpleAxisSerializer
from .ideology_section_serializers import SimpleSectionSerializer
from .ideology_serializers import TargetIdeologySerializer


class AnswerDetailSerializer(serializers.Serializer):
    value = serializers.IntegerField(allow_null=True)
    margin_left = serializers.IntegerField()
    margin_right = serializers.IntegerField()
    is_indifferent = serializers.BooleanField(default=False)


class AxisBreakdownSerializer(serializers.Serializer):
    axis = SimpleAxisSerializer(allow_null=True)
    my_answer = AnswerDetailSerializer(source="user_a", allow_null=True)
    their_answer = AnswerDetailSerializer(source="user_b", allow_null=True)
    affinity = serializers.FloatField(min_value=0.0, max_value=100.0, allow_null=True)


class SectionAffinitySerializer(serializers.Serializer):
    section = SimpleSectionSerializer(allow_null=True)
    affinity = serializers.FloatField(min_value=0.0, max_value=100.0, allow_null=True)
    axes = AxisBreakdownSerializer(many=True)


class ComplexityAffinitySerializer(serializers.Serializer):
    complexity = SimpleComplexitySerializer(allow_null=True)
    affinity = serializers.FloatField(min_value=0.0, max_value=100.0, allow_null=True)
    sections = SectionAffinitySerializer(many=True)


class IdeologyAffinitySerializer(serializers.Serializer):
    target_ideology = TargetIdeologySerializer(read_only=True, allow_null=True)
    total_affinity = serializers.FloatField(
        min_value=0.0,
        max_value=100.0,
        allow_null=True,
        source="total",
        help_text=_("Overall affinity percentage. Null if no common axes."),
    )
    complexities = ComplexityAffinitySerializer(
        many=True, help_text=_("Affinity grouped by abstraction level.")
    )
