from core.helpers import UUIDModelSerializerMixin
from ideology.models import IdeologyAbstractionComplexity


class IdeologyAbstractionComplexitySerializer(UUIDModelSerializerMixin):
    class Meta:
        model = IdeologyAbstractionComplexity
        fields = ["uuid", "name", "description", "complexity"]
