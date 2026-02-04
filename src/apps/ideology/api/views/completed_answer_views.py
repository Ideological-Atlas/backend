from core.api.permissions import IsVerified
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, extend_schema
from ideology.api.serializers import (
    CompletedAnswerSerializer,
    CopyCompletedAnswerSerializer,
)
from ideology.models import CompletedAnswer
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated


@extend_schema(
    tags=["answers"],
    summary=_("Get latest completed answer"),
    description=_(
        "Returns the latest completed answer for the authenticated user as a single object. Returns 404 if no answer exists."
    ),
    responses={200: CompletedAnswerSerializer, 404: None},
)
class LatestCompletedAnswerView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsVerified]
    serializer_class = CompletedAnswerSerializer
    queryset = CompletedAnswer.objects.all()

    def get_object(self):
        return get_object_or_404(
            CompletedAnswer.objects.filter(completed_by=self.request.user).order_by(
                "-created"
            )[:1]
        )


@extend_schema(
    tags=["answers"],
    summary=_("Generate completed answer snapshot"),
    description=_(
        "Generates a snapshot. If logged in, calculates from DB. If anonymous, expects 'axis' and 'conditioners' lists in body."
    ),
    responses={201: CompletedAnswerSerializer},
)
class GenerateCompletedAnswerView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = CompletedAnswerSerializer


@extend_schema(
    tags=["answers"],
    summary=_("Retrieve specific completed answer"),
    description=_("Returns the details of a specific completed answer by its UUID."),
    responses={200: CompletedAnswerSerializer, 404: None},
)
class RetrieveCompletedAnswerView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = CompletedAnswerSerializer
    queryset = CompletedAnswer.objects.all()
    lookup_field = "uuid"


@extend_schema(
    tags=["answers"],
    summary=_("Copy answers from Completed Answer to Profile"),
    description=_(
        "Copies all axis and conditioner answers from a specific Completed Answer to the authenticated user's active profile."
    ),
    request=None,
    responses={201: None},
    parameters=[
        OpenApiParameter(
            name="uuid",
            location=OpenApiParameter.PATH,
            description="UUID of the CompletedAnswer to copy",
            required=True,
            type=str,
        )
    ],
)
class CopyCompletedAnswerToUserView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CopyCompletedAnswerSerializer
    queryset = CompletedAnswer.objects.all()
    lookup_field = "uuid"
