from core.helpers import UUIDModelSerializerMixin
from core.models import User


class SimpleUserSerializer(UUIDModelSerializerMixin):
    class Meta:
        model = User
        fields = ["uuid", "username", "bio", "appearance", "is_public"]
        read_only_fields = ["uuid"]


class PublicUserSerializer(UUIDModelSerializerMixin):
    class Meta:
        model = User
        fields = ["uuid", "username", "bio", "is_public"]
        read_only_fields = ["uuid", "username", "bio", "is_public"]
