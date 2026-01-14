from core.api.exception_handler import custom_exception_handler
from core.exceptions.api_exceptions import BadRequestException
from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import TestCase
from rest_framework.exceptions import ValidationError as DRFValidationError


class ExceptionHandlerTestCase(TestCase):
    def test_handle_django_validation_error(self):
        exc = DjangoValidationError("Invalid data", code="invalid")
        context: dict = {}
        response = custom_exception_handler(exc, context)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 400)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], ["Invalid data"])

    def test_handle_api_base_exception(self):
        exc = BadRequestException("Bad things happened")
        context: dict = {}
        response = custom_exception_handler(exc, context)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "Bad things happened")

    def test_handle_drf_validation_error_formatting(self):
        exc = DRFValidationError(detail="Standard DRF error")
        context: dict = {}
        response = custom_exception_handler(exc, context)
        self.assertIsNotNone(response)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], ["Standard DRF error"])

    def test_unhandled_exception_returns_none(self):
        exc = ZeroDivisionError("Crash")
        context: dict = {}
        response = custom_exception_handler(exc, context)
        self.assertIsNone(response)
