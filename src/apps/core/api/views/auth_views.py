import logging

from core.api.serializers import (
    GoogleLoginSerializer,
    MeSerializer,
    RegisterSerializer,
    UserVerificationSerializer,
)
from core.exceptions import api_exceptions
from core.helpers import UUIUpdateView
from core.models import User
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

logger = logging.getLogger(__name__)


@extend_schema(tags=["auth"], summary=_("Obtain Token Pair (Login)"))
class AuthTokenObtainPairView(TokenObtainPairView):
    pass


@extend_schema(tags=["auth"], summary=_("Refresh Token"))
class AuthTokenRefreshView(TokenRefreshView):
    pass


@extend_schema(tags=["auth"], summary=_("Verify Token"))
class AuthTokenVerifyView(TokenVerifyView):
    pass


@extend_schema(
    tags=["auth"],
    summary=_("Register new user"),
    description=_(
        "Creates a new user account and triggers the verification email process."
    ),
)
class RegisterView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


@extend_schema(
    tags=["auth"],
    summary=_("Verify user account"),
    description=_("Marks a user as verified using their unique UUID."),
    parameters=[
        OpenApiParameter(
            name="uuid",
            description=_("The UUID of the user to verify"),
            required=True,
            location=OpenApiParameter.PATH,
        )
    ],
)
class VerifyUserView(UUIUpdateView):
    permission_classes = [AllowAny]
    serializer_class = UserVerificationSerializer
    queryset = User.objects.all()


@extend_schema(
    tags=["auth"],
    summary=_("Login with Google"),
    description=_(
        "Validates a Google ID Token. Registers the user if they don't exist (verified automatically) and returns JWT tokens."
    ),
    responses={
        200: inline_serializer(
            name="GoogleLoginResponse",
            fields={
                "refresh": serializers.CharField(),
                "access": serializers.CharField(),
                "user": MeSerializer(),
            },
        )
    },
)
class GoogleLoginView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = GoogleLoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]

        try:
            user, created = User.objects.get_or_create_from_google_token(token)

            if not user.is_active:
                raise api_exceptions.ForbiddenException(_("User account is disabled."))

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": MeSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            logger.warning("Google Login Error: %s", e)
            raise api_exceptions.BadRequestException(str(e))
