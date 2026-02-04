from core.api.serializers.geo_serializers import CountrySerializer, RegionSerializer
from core.helpers import UUIDModelSerializerMixin
from ideology.models import Ideology

from .ideology_axis_definition_serializers import IdeologyAxisDefinitionSerializer
from .ideology_conditioner_definition_serializers import (
    IdeologyConditionerDefinitionSerializer,
)
from .religion_serializers import ReligionSerializer
from .tag_serializers import TagSerializer


class IdeologyListSerializer(UUIDModelSerializerMixin):
    tags = TagSerializer(many=True, read_only=True)
    associated_countries = CountrySerializer(many=True, read_only=True)
    associated_regions = RegionSerializer(many=True, read_only=True)
    associated_religions = ReligionSerializer(many=True, read_only=True)

    class Meta:
        model = Ideology
        fields = [
            "uuid",
            "name",
            "description_supporter",
            "description_detractor",
            "description_neutral",
            "flag",
            "background",
            "color",
            "tags",
            "associated_countries",
            "associated_regions",
            "associated_religions",
        ]


class IdeologyDetailSerializer(UUIDModelSerializerMixin):
    axis_definitions = IdeologyAxisDefinitionSerializer(many=True, read_only=True)
    conditioner_definitions = IdeologyConditionerDefinitionSerializer(
        many=True, read_only=True
    )
    tags = TagSerializer(many=True, read_only=True)
    associated_countries = CountrySerializer(many=True, read_only=True)
    associated_regions = RegionSerializer(many=True, read_only=True)
    associated_religions = ReligionSerializer(many=True, read_only=True)

    class Meta:
        model = Ideology
        fields = [
            "uuid",
            "name",
            "description_supporter",
            "description_detractor",
            "description_neutral",
            "flag",
            "background",
            "color",
            "axis_definitions",
            "conditioner_definitions",
            "tags",
            "associated_countries",
            "associated_regions",
            "associated_religions",
        ]


class TargetIdeologySerializer(UUIDModelSerializerMixin):
    class Meta:
        model = Ideology
        fields = [
            "uuid",
            "name",
            "description_supporter",
            "description_detractor",
            "description_neutral",
            "flag",
            "background",
            "color",
        ]
