from core.api.permissions import IsVerified
from core.helpers import UUIDDestroyAPIView
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, extend_schema
from ideology.api.serializers import (
    AxisAnswerReadSerializer,
    AxisAnswerUpsertSerializer,
)
from ideology.models import UserAxisAnswer
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@extend_schema(
    tags=["answers"],
    summary=_("Upsert axis answer"),
    description=_(
        "Creates or updates the user's answer for a specific axis defined by UUID in URL. "
        "Allows marking answer as indifferent (null value)."
    ),
    parameters=[
        OpenApiParameter(
            name="uuid",
            location=OpenApiParameter.PATH,
            description="UUID of the Axis to answer",
            required=True,
            type=str,
        )
    ],
    responses={201: AxisAnswerReadSerializer},
)
class UpsertAxisAnswerView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsVerified]
    serializer_class = AxisAnswerUpsertSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        read_serializer = AxisAnswerReadSerializer(instance)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["answers"],
    summary=_("Delete axis answer"),
    description=_(
        "Deletes the user's answer for the specific axis defined by UUID in URL."
    ),
    responses={204: None},
    parameters=[
        OpenApiParameter(
            name="uuid",
            location=OpenApiParameter.PATH,
            description="UUID of the Axis whose answer you want to delete",
            required=True,
            type=str,
        )
    ],
)
class DeleteAxisAnswerView(UUIDDestroyAPIView):
    permission_classes = [IsAuthenticated, IsVerified]

    def get_object(self):
        axis_uuid = self.kwargs.get(self.lookup_field)
        return get_object_or_404(
            UserAxisAnswer, user=self.request.user, axis__uuid=axis_uuid
        )


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
            return UserAxisAnswer.objects.none()

        section_uuid = self.kwargs.get("section_uuid")
        return UserAxisAnswer.objects.filter(
            user=self.request.user, axis__section__uuid=section_uuid
        ).select_related("axis")
