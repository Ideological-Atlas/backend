from core.exceptions.api_exceptions import ApiBaseException
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def custom_exception_handler(exc, context):
    if isinstance(exc, DjangoValidationError):
        data = {"message": exc.messages}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    response = drf_exception_handler(exc, context)
    if response is not None:
        if isinstance(exc, ApiBaseException):
            return response
        if isinstance(response.data, list):
            response.data = {"message": response.data}
        elif isinstance(response.data, dict):
            if "detail" in response.data:
                response.data["message"] = response.data.pop("detail")
    return response
