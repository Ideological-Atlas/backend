from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, extend_schema
from ideology.api.serializers import (
    IdeologyConditionerDefinitionSerializer,
    IdeologyConditionerDefinitionUpsertSerializer,
)
from ideology.models import IdeologyConditionerDefinition
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated


@extend_schema(
    tags=["ideologies"],
    summary=_("List conditioner definitions by ideology"),
    description=_("Returns the conditioner definitions for a specific ideology."),
    parameters=[
        OpenApiParameter(
            name="ideology_uuid",
            location=OpenApiParameter.PATH,
            description="UUID of the Ideology",
            required=True,
            type=str,
        )
    ],
)
class IdeologyConditionerDefinitionListByIdeologyView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = IdeologyConditionerDefinitionSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return IdeologyConditionerDefinition.objects.none()

        ideology_uuid = self.kwargs.get("ideology_uuid")
        return IdeologyConditionerDefinition.objects.filter(
            ideology__uuid=ideology_uuid
        ).select_related("conditioner")


@extend_schema(
    tags=["ideologies"],
    summary=_("Upsert ideology conditioner definition"),
    description=_(
        "Creates or updates the conditioner definition for a specific ideology. Requires admin permissions."
    ),
    parameters=[
        OpenApiParameter(
            name="ideology_uuid",
            location=OpenApiParameter.PATH,
            description="UUID of the Ideology",
            required=True,
            type=str,
        ),
        OpenApiParameter(
            name="conditioner_uuid",
            location=OpenApiParameter.PATH,
            description="UUID of the Conditioner",
            required=True,
            type=str,
        ),
    ],
    responses={201: IdeologyConditionerDefinitionSerializer},
)
class UpsertIdeologyConditionerDefinitionView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = IdeologyConditionerDefinitionUpsertSerializer
