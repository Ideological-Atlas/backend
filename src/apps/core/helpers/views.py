from rest_framework.generics import UpdateAPIView


class UUIUpdateView(UpdateAPIView):
    lookup_field = "uuid"
