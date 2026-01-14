from core.api.permissions import IsVerified
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from ideology.api.serializers import CompletedAnswerSerializer
from ideology.models import CompletedAnswer
from ideology.services import AnswerService
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


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
        "Triggers the calculation of the user's current results, saves it as a CompletedAnswer, and returns the structured data."
    ),
    request=None,
    responses={201: CompletedAnswerSerializer},
)
class GenerateCompletedAnswerView(APIView):
    permission_classes = [IsAuthenticated, IsVerified]

    def post(self, request):
        completed_answer = AnswerService.generate_snapshot(user=request.user)
        serializer = CompletedAnswerSerializer(completed_answer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
