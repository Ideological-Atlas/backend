from core.api.permissions import IsVerified
from core.exceptions.api_exceptions import NotFoundException
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class BaseUpsertAnswerView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsVerified]

    read_serializer_class: type[serializers.Serializer] | None = None
    write_serializer_class: type[serializers.Serializer] | None = None

    target_model: type[models.Model] | None = None
    reference_model: type[models.Model] | None = None

    reference_field: str = ""
    lookup_url_kwarg: str = "uuid"
    request_value_key: str = ""
    target_value_key: str = ""

    created_object: models.Model | None = None

    def get_serializer_class(self) -> type[serializers.Serializer]:
        if (
            self.request.method == "POST"
            and self.created_object
            and self.read_serializer_class
        ):
            return self.read_serializer_class

        if self.write_serializer_class:
            return self.write_serializer_class

        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        if not self.target_model or not self.reference_model:
            raise NotImplementedError("target_model and reference_model must be set")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uuid_value = self.kwargs.get(self.lookup_url_kwarg)
        input_value = serializer.validated_data[self.request_value_key]

        reference_manager = getattr(self.reference_model, "objects")  # type: ignore
        reference_obj = reference_manager.filter(uuid=uuid_value).first()

        if not reference_obj:
            raise NotFoundException(
                _("{model} not found").format(model=self.reference_model.__name__)
            )

        lookup_kwargs = {"user": request.user, self.reference_field: reference_obj}

        target_manager = getattr(self.target_model, "objects")  # type: ignore
        self.created_object, created = target_manager.update_or_create(
            **lookup_kwargs, defaults={self.target_value_key: input_value}
        )

        read_serializer = self.get_serializer(self.created_object)

        return Response(
            read_serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
