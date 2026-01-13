from core.api.permissions import IsVerified
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, extend_schema
from ideology.api.serializers import (
    ConditionerAnswerReadSerializer,
    ConditionerAnswerUpsertSerializer,
)
from ideology.models import ConditionerAnswer, IdeologyConditioner
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from .base_views import BaseUpsertAnswerView


@extend_schema(
    tags=["answers"],
    summary=_("Upsert conditioner answer"),
    description=_(
        "Creates or updates the user's answer for a specific conditioner defined by UUID in URL."
    ),
    request=ConditionerAnswerUpsertSerializer,
    responses={200: ConditionerAnswerReadSerializer},
    parameters=[
        OpenApiParameter(
            name="uuid",
            location=OpenApiParameter.PATH,
            description="UUID of the Conditioner to answer",
            required=True,
            type=str,
        )
    ],
)
class UpsertConditionerAnswerView(BaseUpsertAnswerView):
    write_serializer_class = ConditionerAnswerUpsertSerializer
    read_serializer_class = ConditionerAnswerReadSerializer

    target_model = ConditionerAnswer
    reference_model = IdeologyConditioner

    reference_field = "conditioner"
    request_value_key = "answer"
    target_value_key = "answer"


@extend_schema(
    tags=["answers"],
    summary=_("List user conditioner answers by complexity"),
    description=_(
        "Returns the user's conditioner answers filtered by abstraction complexity (via sections or axes)."
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
class UserConditionerAnswerListByComplexityView(ListAPIView):
    permission_classes = [IsAuthenticated, IsVerified]
    serializer_class = ConditionerAnswerReadSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return ConditionerAnswer.objects.none()

        complexity_uuid = self.kwargs.get("complexity_uuid")

        return (
            ConditionerAnswer.objects.filter(user=self.request.user)
            .filter(
                Q(
                    conditioner__section_rules__section__abstraction_complexity__uuid=complexity_uuid
                )
                | Q(
                    conditioner__axis_rules__axis__section__abstraction_complexity__uuid=complexity_uuid
                )
            )
            .select_related("conditioner")
            .distinct()
        )
