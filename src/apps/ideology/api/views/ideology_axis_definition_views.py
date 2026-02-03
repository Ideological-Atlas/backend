from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, extend_schema
from ideology.api.serializers import (
    IdeologyAxisDefinitionSerializer,
    IdeologyAxisDefinitionUpsertSerializer,
)
from ideology.models import IdeologyAxisDefinition
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated


@extend_schema(
    tags=["ideologies"],
    summary=_("List axis definitions by ideology"),
    description=_("Returns the axis definitions for a specific ideology."),
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
class IdeologyAxisDefinitionListByIdeologyView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = IdeologyAxisDefinitionSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return IdeologyAxisDefinition.objects.none()

        ideology_uuid = self.kwargs.get("ideology_uuid")
        return IdeologyAxisDefinition.objects.filter(
            ideology__uuid=ideology_uuid
        ).select_related("axis")


@extend_schema(
    tags=["ideologies"],
    summary=_("Upsert ideology axis definition"),
    description=_(
        "Creates or updates the definition for a specific ideology and axis. Requires admin permissions."
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
            name="axis_uuid",
            location=OpenApiParameter.PATH,
            description="UUID of the Axis",
            required=True,
            type=str,
        ),
    ],
    responses={201: IdeologyAxisDefinitionSerializer},
)
class UpsertIdeologyAxisDefinitionView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = IdeologyAxisDefinitionUpsertSerializer


@extend_schema(
    tags=["ideologies"],
    summary=_("Delete ideology axis definition"),
    description=_(
        "Deletes the definition for a specific ideology and axis. Requires admin permissions."
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
            name="axis_uuid",
            location=OpenApiParameter.PATH,
            description="UUID of the Axis",
            required=True,
            type=str,
        ),
    ],
    responses={204: None},
)
class DeleteIdeologyAxisDefinitionView(DestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self):
        return get_object_or_404(
            IdeologyAxisDefinition,
            ideology__uuid=self.kwargs["ideology_uuid"],
            axis__uuid=self.kwargs["axis_uuid"],
        )
