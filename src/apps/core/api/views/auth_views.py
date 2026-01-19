import logging

from core.api.serializers import (
    CustomTokenObtainPairSerializer,
    GoogleLoginSerializer,
    MeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    UserVerificationSerializer,
)
from core.exceptions import api_exceptions
from core.exceptions.user_exceptions import UserDisabledException
from core.helpers import UUIDUpdateAPIView
from core.models import User
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
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
        "Creates a new user account, triggers verification email via Manager, and logs the user in automatically."
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

        user = User.objects.register(serializer.validated_data)

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
            user = User.objects.login_with_google(token)
        except ValueError as error:
            raise api_exceptions.BadRequestException(str(error))
        except UserDisabledException:
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


@extend_schema(
    tags=["auth"],
    summary=_("Request Password Reset"),
    description=_(
        "Triggers a password reset email if the email exists. Always returns 200 OK for security."
    ),
    responses={
        200: inline_serializer(
            name="PasswordResetResponse",
            fields={"message": serializers.CharField()},
        )
    },
)
class PasswordResetRequestView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        User.objects.request_password_reset(email=serializer.validated_data["email"])
        return Response(
            {"message": _("If the email exists, a password reset link has been sent.")},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["auth"],
    summary=_("Check Reset Token Validity"),
    description=_("Checks if a reset password token exists and is valid."),
    responses={200: None, 404: None},
)
class PasswordResetVerifyTokenView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uuid):
        User.objects.verify_reset_token(uuid)
        return Response(status=status.HTTP_200_OK)


@extend_schema(
    tags=["auth"],
    summary=_("Confirm Password Reset"),
    description=_("Resets the user's password using the token and invalidates it."),
    responses={200: None},
)
class PasswordResetConfirmView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, uuid):
        user = User.objects.verify_reset_token(uuid)
        serializer = self.get_serializer(data=request.data, context={"user": user})
        serializer.is_valid(raise_exception=True)
        User.objects.confirm_password_reset(
            token=uuid, new_password=serializer.validated_data["new_password"]
        )

        return Response(
            {"message": _("Password has been reset successfully.")},
            status=status.HTTP_200_OK,
        )
