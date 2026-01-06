from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, extend_schema
from ideology.api.serializers import IdeologyAxisSerializer
from ideology.models import IdeologyAxis
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny


@extend_schema(
    tags=["structure"],
    summary=_("List axes by section"),
    description=_(
        "Returns all axes (including their conditioners) for a specific section UUID."
    ),
    parameters=[
        OpenApiParameter(
            name="section_uuid",
            location=OpenApiParameter.PATH,
            description="UUID of the Ideology Section",
            required=True,
            type=str,
        )
    ],
)
class AxisListBySectionView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = IdeologyAxisSerializer

    def get_queryset(self):
        section_uuid = self.kwargs.get("section_uuid")
        return (
            IdeologyAxis.objects.filter(section__uuid=section_uuid)
            .select_related("conditioned_by")
            .order_by("name")
        )
