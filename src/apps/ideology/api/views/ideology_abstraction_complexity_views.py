from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from ideology.api.serializers import IdeologyAbstractionComplexitySerializer
from ideology.models import IdeologyAbstractionComplexity
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny


@extend_schema(
    tags=["structure"],
    summary=_("List all abstraction complexities"),
    description=_("Returns a list of all available complexity levels for the test."),
)
class AbstractionComplexityListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = IdeologyAbstractionComplexitySerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return IdeologyAbstractionComplexity.objects.all().order_by("complexity")
        return IdeologyAbstractionComplexity.objects.visible.order_by("complexity")
