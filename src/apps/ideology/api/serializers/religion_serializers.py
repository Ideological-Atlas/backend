from core.helpers import UUIDModelSerializerMixin
from ideology.models import Religion


class ReligionSerializer(UUIDModelSerializerMixin):
    class Meta:
        model = Religion
        fields = ["uuid", "name", "description"]
