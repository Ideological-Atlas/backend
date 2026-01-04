from core.api.serializers import (
    MeSerializer,
    RegisterSerializer,
    UserVerificationSerializer,
)
from core.helpers import UUIUpdateView
from core.models import User
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated


@extend_schema(
    tags=["users"],
    summary=_("Register new user"),
    description=_(
        "Creates a new user account and triggers the verification email process."
    ),
)
class RegisterView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


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
