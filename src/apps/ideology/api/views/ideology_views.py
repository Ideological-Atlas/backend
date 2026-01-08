from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters
from drf_spectacular.utils import OpenApiParameter, extend_schema
from ideology.api.serializers import IdeologyDetailSerializer, IdeologyListSerializer
from ideology.models import Ideology
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny


class IdeologyFilter(filters.FilterSet):
    country = filters.NumberFilter(field_name="associated_countries__id")
    region = filters.NumberFilter(field_name="associated_regions__id")
    religion = filters.UUIDFilter(field_name="associated_religions__uuid")
    tag = filters.UUIDFilter(field_name="tags__uuid")

    class Meta:
        model = Ideology
        fields = ["country", "region", "religion", "tag"]


@extend_schema(
    tags=["ideologies"],
    summary=_("List all ideologies"),
    description=_(
        "Returns a paginated list of ideologies. Supports filtering by related entities and text search."
    ),
    parameters=[
        OpenApiParameter(
            name="search",
            description=_("Search by name or descriptions"),
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="country",
            description=_("Filter by Country ID (Integer)"),
            required=False,
            type=int,
        ),
        OpenApiParameter(
            name="region",
            description=_("Filter by Region ID (Integer)"),
            required=False,
            type=int,
        ),
        OpenApiParameter(
            name="religion",
            description=_("Filter by Religion UUID"),
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="tag", description=_("Filter by Tag UUID"), required=False, type=str
        ),
    ],
)
class IdeologyListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = IdeologyListSerializer
    queryset = Ideology.objects.all().order_by("name").distinct()
    filter_backends = [filters.DjangoFilterBackend, SearchFilter]
    filterset_class = IdeologyFilter
    search_fields = [
        "name",
        "description_supporter",
        "description_detractor",
        "description_neutral",
    ]


@extend_schema(
    tags=["ideologies"],
    summary=_("Get ideology details"),
    description=_(
        "Returns details of a specific ideology including its definition values (axis and conditioners)."
    ),
)
class IdeologyDetailView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = IdeologyDetailSerializer
    queryset = Ideology.objects.all()
    lookup_field = "uuid"
