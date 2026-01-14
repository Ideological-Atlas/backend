from core.api.permissions import IsVerified
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, extend_schema
from ideology.api.serializers import (
    ConditionerAnswerReadSerializer,
    ConditionerAnswerUpsertSerializer,
)
from ideology.models import UserConditionerAnswer
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@extend_schema(
    tags=["answers"],
    summary=_("Upsert conditioner answer"),
    description=_(
        "Creates or updates the user's answer for a specific conditioner defined by UUID in URL."
    ),
    parameters=[
        OpenApiParameter(
            name="uuid",
            location=OpenApiParameter.PATH,
            description="UUID of the Conditioner to answer",
            required=True,
            type=str,
        )
    ],
    responses={201: ConditionerAnswerReadSerializer},
)
class UpsertConditionerAnswerView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsVerified]
    serializer_class = ConditionerAnswerUpsertSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        read_serializer = ConditionerAnswerReadSerializer(instance)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)


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
            return UserConditionerAnswer.objects.none()

        complexity_uuid = self.kwargs.get("complexity_uuid")

        return (
            UserConditionerAnswer.objects.filter(user=self.request.user)
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
