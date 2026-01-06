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
    queryset = IdeologyAbstractionComplexity.objects.all().order_by("complexity")
    serializer_class = IdeologyAbstractionComplexitySerializer
