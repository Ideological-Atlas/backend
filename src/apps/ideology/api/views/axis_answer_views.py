from core.api.permissions import IsVerified
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, extend_schema
from ideology.api.serializers import (
    AxisAnswerReadSerializer,
    AxisAnswerUpsertSerializer,
)
from ideology.models import AxisAnswer, IdeologyAxis
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from .base_views import BaseUpsertAnswerView


@extend_schema(
    tags=["answers"],
    summary=_("Upsert axis answer"),
    description=_(
        "Creates or updates the user's answer for a specific axis defined by UUID in URL."
    ),
    request=AxisAnswerUpsertSerializer,
    responses={200: AxisAnswerReadSerializer},
    parameters=[
        OpenApiParameter(
            name="uuid",
            location=OpenApiParameter.PATH,
            description="UUID of the Axis to answer",
            required=True,
            type=str,
        )
    ],
)
class UpsertAxisAnswerView(BaseUpsertAnswerView):
    write_serializer_class = AxisAnswerUpsertSerializer
    read_serializer_class = AxisAnswerReadSerializer

    target_model = AxisAnswer
    reference_model = IdeologyAxis

    reference_field = "axis"

    def get_defaults(self, serializer) -> dict:
        data = serializer.validated_data
        return {
            "value": data["value"],
            "margin_left": data.get("margin_left", 0),
            "margin_right": data.get("margin_right", 0),
        }


@extend_schema(
    tags=["answers"],
    summary=_("List user axis answers by section"),
    description=_(
        "Returns the user's axis answers filtered by a specific ideology section."
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
class UserAxisAnswerListBySectionView(ListAPIView):
    permission_classes = [IsAuthenticated, IsVerified]
    serializer_class = AxisAnswerReadSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return AxisAnswer.objects.none()

        section_uuid = self.kwargs.get("section_uuid")
        return AxisAnswer.objects.filter(
            user=self.request.user, axis__section__uuid=section_uuid
        ).select_related("axis")
