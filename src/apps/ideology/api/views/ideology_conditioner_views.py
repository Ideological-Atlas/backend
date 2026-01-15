from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, extend_schema
from ideology.api.serializers import IdeologyConditionerSerializer
from ideology.models import IdeologyConditioner, IdeologyConditionerConditioner
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny


@extend_schema(
    tags=["structure"],
    summary=_("List all relevant conditioners by complexity"),
    description=_(
        "Returns ALL conditioners relevant for a complexity level. This includes conditioners attached to sections, axes, AND recursive dependencies (conditioners required by other conditioners)."
    ),
    parameters=[
        OpenApiParameter(
            name="complexity_uuid",
            location=OpenApiParameter.PATH,
            description="UUID of the Abstraction Complexity",
            required=True,
            type=str,
        )
    ],
)
class ConditionerListAggregatedByComplexityView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = IdeologyConditionerSerializer

    def get_queryset(self):
        complexity_uuid = self.kwargs.get("complexity_uuid")

        relevant_ids = set(
            IdeologyConditioner.objects.filter(
                Q(section_rules__section__abstraction_complexity__uuid=complexity_uuid)
                | Q(
                    axis_rules__axis__section__abstraction_complexity__uuid=complexity_uuid
                )
            ).values_list("id", flat=True)
        )

        current_level_ids = list(relevant_ids)

        while current_level_ids:
            parent_dependencies = IdeologyConditionerConditioner.objects.filter(
                target_conditioner__id__in=current_level_ids
            ).values_list("source_conditioner_id", flat=True)

            new_parent_ids = set(parent_dependencies) - relevant_ids

            if not new_parent_ids:
                break

            relevant_ids.update(new_parent_ids)
            current_level_ids = list(new_parent_ids)

        return IdeologyConditioner.objects.filter(id__in=relevant_ids).order_by("name")
