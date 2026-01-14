from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, extend_schema
from ideology.api.serializers import IdeologyConditionerSerializer
from ideology.models import IdeologyConditioner
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny


@extend_schema(
    tags=["structure"],
    summary=_("List all relevant conditioners by complexity"),
    description=_(
        "Returns ALL conditioners relevant for a complexity level. This includes conditioners attached to sections AND conditioners attached to axes within those sections."
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
        return (
            IdeologyConditioner.objects.filter(
                Q(section_rules__section__abstraction_complexity__uuid=complexity_uuid)
                | Q(
                    axis_rules__axis__section__abstraction_complexity__uuid=complexity_uuid
                )
            )
            .distinct()
            .order_by("name")
        )
