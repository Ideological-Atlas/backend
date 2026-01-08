from rest_framework import status
from rest_framework.exceptions import APIException


class ApiBaseException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "A server error occurred."
    default_code = "error"

    def __init__(self, message=None, **kwargs):
        if message is None:
            message = self.default_detail

        if isinstance(message, Exception):
            message = str(message)

        final_detail = {"message": message, "type": self.__class__.__name__, **kwargs}

        super().__init__(detail=final_detail)


class BadRequestException(ApiBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Bad request exception"
    default_code = "bad request"


class ConflictException(ApiBaseException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Conflict exception"
    default_code = "conflict"


class ForbiddenException(ApiBaseException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Forbidden exception"
    default_code = "forbidden"


class PaymentRequiredException(ApiBaseException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = "Payment required exception"
    default_code = "payment required"


class NotAcceptableException(ApiBaseException):
    status_code = status.HTTP_406_NOT_ACCEPTABLE
    default_detail = "Not acceptable exception"
    default_code = "not acceptable"


class NotFoundException(ApiBaseException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Not found exception"
    default_code = "not found"


class PreconditionFailedException(ApiBaseException):
    status_code = status.HTTP_412_PRECONDITION_FAILED
    default_detail = "Precondition failed exception"
    default_code = "precondition failed"


class TooEarlyException(ApiBaseException):
    status_code = status.HTTP_425_TOO_EARLY
    default_detail = "Too early exception"
    default_code = "too early"
