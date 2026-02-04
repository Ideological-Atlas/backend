from core.api.serializers import CountrySerializer, RegionSerializer
from core.models import Country, Region
from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny


@extend_schema(
    tags=["geography"],
    summary=_("List all countries"),
    description=_("List available countries from the database."),
    parameters=[
        OpenApiParameter(
            name="search", description=_("Search by name"), required=False, type=str
        ),
    ],
)
class CountryListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CountrySerializer
    queryset = Country.objects.all().order_by("name")
    filter_backends = [SearchFilter]
    search_fields = ["name", "code2"]


@extend_schema(
    tags=["geography"],
    summary=_("List regions"),
    description=_("List regions, optionally filtered by country."),
    parameters=[
        OpenApiParameter(
            name="country_id",
            description=_("Filter by Country ID"),
            required=False,
            type=int,
        ),
        OpenApiParameter(
            name="search", description=_("Search by name"), required=False, type=str
        ),
    ],
)
class RegionListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegionSerializer
    filter_backends = [filters.DjangoFilterBackend, SearchFilter]
    search_fields = ["name"]

    def get_queryset(self):
        qs = Region.objects.all().order_by("name")
        country_id = self.request.query_params.get("country_id")
        if country_id:
            qs = qs.filter(country_id=country_id)
        return qs
