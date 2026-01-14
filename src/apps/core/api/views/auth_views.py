import logging

from core.api.serializers import (
    CustomTokenObtainPairSerializer,
    GoogleLoginSerializer,
    MeSerializer,
    RegisterSerializer,
    UserVerificationSerializer,
)
from core.exceptions import api_exceptions
from core.helpers import UUIDUpdateAPIView
from core.models import User
from core.services import AuthService
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


@extend_schema(
    tags=["auth"],
    summary=_("Obtain Token Pair (Login)"),
    responses={
        200: inline_serializer(
            name="TokenObtainPairResponse",
            fields={
                "access": serializers.CharField(),
                "refresh": serializers.CharField(),
                "user": MeSerializer(),
            },
        )
    },
)
class AuthTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


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
        "Creates a new user account, triggers verification email via Service, and logs the user in automatically."
    ),
    responses={
        201: inline_serializer(
            name="RegisterResponse",
            fields={
                "access": serializers.CharField(),
                "refresh": serializers.CharField(),
                "user": MeSerializer(),
            },
        )
    },
)
class RegisterView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = AuthService.register_user(serializer.validated_data)

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": MeSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=["auth"],
    summary=_("Verify user account"),
    description=_("Marks a user as verified using their secret verification token."),
    parameters=[
        OpenApiParameter(
            name="uuid",
            description=_("The verification UUID sent via email"),
            required=True,
            location=OpenApiParameter.PATH,
        )
    ],
)
class VerifyUserView(UUIDUpdateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserVerificationSerializer
    queryset = User.objects.all()
    lookup_field = "verification_uuid"


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
            raise api_exceptions.BadRequestException(str(e))
