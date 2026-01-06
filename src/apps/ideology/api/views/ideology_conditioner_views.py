from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, extend_schema
from ideology.api.serializers import IdeologyConditionerSerializer
from ideology.models import IdeologyConditioner
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny


@extend_schema(
    tags=["structure"],
    summary=_("List conditioners by complexity"),
    description=_(
        "Returns all ideology conditioners associated with a specific abstraction complexity UUID."
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
class ConditionerListByComplexityView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = IdeologyConditionerSerializer

    def get_queryset(self):
        complexity_uuid = self.kwargs.get("complexity_uuid")
        return IdeologyConditioner.objects.filter(
            abstraction_complexity__uuid=complexity_uuid
        ).order_by("name")
