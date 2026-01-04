from core.exceptions import api_exceptions, user_exceptions
from django.test import TestCase
from rest_framework import status


class ExceptionsTestCase(TestCase):
    def test_api_base_exception_structure(self):
        exc = api_exceptions.ApiBaseException(message="Error", extra="1")
        self.assertEqual(exc.detail["message"], "Error")

        native = ValueError("Native")
        self.assertEqual(
            api_exceptions.ApiBaseException(message=native).detail["message"], "Native"
        )

    def test_status_codes_mapping(self):
        exception_map = [
            (api_exceptions.BadRequestException, status.HTTP_400_BAD_REQUEST),
            (api_exceptions.ConflictException, status.HTTP_409_CONFLICT),
            (api_exceptions.ForbiddenException, status.HTTP_403_FORBIDDEN),
            (api_exceptions.PaymentRequiredException, status.HTTP_402_PAYMENT_REQUIRED),
            (api_exceptions.NotAcceptableException, status.HTTP_406_NOT_ACCEPTABLE),
            (api_exceptions.NotFoundException, status.HTTP_404_NOT_FOUND),
            (
                api_exceptions.PreconditionFailedException,
                status.HTTP_412_PRECONDITION_FAILED,
            ),
            (api_exceptions.TooEarlyException, status.HTTP_425_TOO_EARLY),
        ]
        for exc_cls, st in exception_map:
            with self.subTest(exc=exc_cls.__name__):
                self.assertEqual(exc_cls().status_code, st)

    def test_user_exceptions(self):
        exc = user_exceptions.UserAlreadyVerifiedException("UserX")
        self.assertIn("UserX", str(exc))
        exc = user_exceptions.UserAlreadyVerifiedException(None)
        self.assertEqual("User not verified", str(exc))
