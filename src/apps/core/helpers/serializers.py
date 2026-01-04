from rest_framework import serializers


class UUIDModelSerializerMixin(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format="hex", read_only=True)
