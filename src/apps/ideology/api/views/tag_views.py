from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, extend_schema
from ideology.api.serializers import TagSerializer
from ideology.models import Tag
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny


@extend_schema(
    tags=["ideologies"],
    summary=_("List all tags"),
    description=_("Returns a list of all available tags."),
    parameters=[
        OpenApiParameter(
            name="search", description=_("Search by name"), required=False, type=str
        ),
    ],
)
class TagListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = TagSerializer
    queryset = Tag.objects.all().order_by("name")
    filter_backends = [SearchFilter]
    search_fields = ["name"]
