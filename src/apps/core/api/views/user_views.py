from core.api.serializers import (
    MeSerializer,
    RegisterSerializer,
    UserVerificationSerializer,
)
from core.helpers import UUIUpdateView
from core.models import User
from drf_spectacular.utils import extend_schema
from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated


@extend_schema(
    tags=["users"],
)
class RegisterView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


@extend_schema(
    tags=["users"],
)
class MeDetailView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MeSerializer

    def get_object(self):
        return self.request.user


@extend_schema(tags=["users"])
class VerifyUserView(UUIUpdateView):
    permission_classes = [AllowAny]
    serializer_class = UserVerificationSerializer
    queryset = User.objects.all()
