from core.api.permissions import IsVerified
from core.api.serializers import (
    AffinitySerializer,
    MeSerializer,
    UserSetPasswordSerializer,
)
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from ideology.models import CompletedAnswer
from rest_framework import status
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@extend_schema(
    tags=["users"],
    summary=_("Get or update current profile"),
    description=_(
        "Retrieve the profile information of the currently authenticated user "
        "or update their details."
    ),
)
class MeDetailView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MeSerializer

    def get_object(self):
        return self.request.user


@extend_schema(
    tags=["users"],
    summary=_("Set user password"),
    description=_(
        "Allows an authenticated user (e.g., logged in via Google) to set a password "
        "so they can use standard login in the future."
    ),
    responses={200: MeSerializer},
)
class UserSetPasswordView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSetPasswordSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(MeSerializer(user).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["users"],
    summary=_("Get affinity with a Completed Answer"),
    description=_(
        "Calculates the ideological affinity (0-100%) between the current user's active answers "
        "and a specific CompletedAnswer (identified by UUID). The target might be anonymous."
    ),
)
class UserAffinityView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsVerified]
    queryset = CompletedAnswer.objects.all()
    lookup_field = "uuid"
    serializer_class = AffinitySerializer

    def get(self, request, *args, **kwargs):
        target_answer = self.get_object()
        data = request.user.calculate_detailed_affinity_with(target_answer)
        serializer = self.get_serializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
