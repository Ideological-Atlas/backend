from core.helpers import UUIDModelSerializerMixin
from ideology.models import Tag


class TagSerializer(UUIDModelSerializerMixin):
    class Meta:
        model = Tag
        fields = ["uuid", "name", "description"]
