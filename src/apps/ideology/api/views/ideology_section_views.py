from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, extend_schema
from ideology.api.serializers import IdeologySectionSerializer
from ideology.models import IdeologySection
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny


@extend_schema(
    tags=["structure"],
    summary=_("List sections by complexity"),
    description=_(
        "Returns all sections associated with a specific abstraction complexity UUID."
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
class SectionListByComplexityView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = IdeologySectionSerializer

    def get_queryset(self):
        complexity_uuid = self.kwargs.get("complexity_uuid")
        return (
            IdeologySection.objects.filter(abstraction_complexity__uuid=complexity_uuid)
            .prefetch_related("condition_rules__conditioner")
            .order_by("created")
        )
