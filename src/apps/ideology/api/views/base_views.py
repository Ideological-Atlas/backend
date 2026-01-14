from core.exceptions.api_exceptions import NotFoundException
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response


class BaseUpsertAnswerView(CreateAPIView):
    reference_model = None
    target_model = None
    request_uuid_key = "uuid"
    request_value_key = "value"
    target_value_key = "value"
    reference_field = None
    lookup_url_kwarg = "uuid"
    created_object = None

    def get_serializer_class(self):
        if hasattr(self, "write_serializer_class") and self.write_serializer_class:
            return self.write_serializer_class
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        if not self.reference_model or not self.target_model:
            raise NotImplementedError("Configuration missing")

        uuid_val = self.kwargs.get(self.lookup_url_kwarg)
        ref_obj = self.reference_model.objects.filter(uuid=uuid_val).first()

        if not ref_obj:
            raise NotFoundException(
                _("{model} not found").format(model=self.reference_model.__name__)
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        value = serializer.validated_data.get(self.request_value_key)

        defaults = {self.target_value_key: value}
        lookup = {"user": request.user, self.reference_field: ref_obj}

        self.created_object, created = self.target_model.objects.update_or_create(
            **lookup, defaults=defaults
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)
