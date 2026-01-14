from rest_framework.generics import DestroyAPIView, UpdateAPIView


class UUIDUpdateAPIView(UpdateAPIView):
    lookup_field = "uuid"


class UUIDDestroyAPIView(DestroyAPIView):
    lookup_field = "uuid"
