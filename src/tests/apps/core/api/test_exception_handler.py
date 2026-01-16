from unittest.mock import patch

from core.api.exception_handler import custom_exception_handler
from core.exceptions.api_exceptions import BadRequestException
from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import TestCase
from rest_framework.exceptions import APIException
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response


class ExceptionHandlerTestCase(TestCase):
    def test_handle_django_validation_error(self):
        exc = DjangoValidationError("Invalid data", code="invalid")
        response = custom_exception_handler(exc, {})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 400)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], ["Invalid data"])

    def test_handle_api_base_exception(self):
        exc = BadRequestException("Bad things happened")
        response = custom_exception_handler(exc, {})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "Bad things happened")

    def test_handle_drf_validation_error_formatting(self):
        exc = DRFValidationError(detail="Standard DRF error")
        response = custom_exception_handler(exc, {})
        self.assertIsNotNone(response)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], ["Standard DRF error"])

    @patch("core.api.exception_handler.drf_exception_handler")
    def test_handle_generic_drf_exception_with_detail_field(self, mock_drf_handler):
        mock_drf_handler.return_value = Response(
            {"detail": "Generic Error"}, status=418
        )

        exc = APIException("Some generic error")
        response = custom_exception_handler(exc, {})

        self.assertIsNotNone(response)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "Generic Error")
        self.assertNotIn("detail", response.data)

    @patch("core.api.exception_handler.drf_exception_handler")
    def test_handle_generic_drf_exception_without_detail_field(self, mock_drf_handler):
        mock_drf_handler.return_value = Response(
            {"other_field": "Something"}, status=418
        )

        exc = APIException("Some generic error")
        response = custom_exception_handler(exc, {})

        self.assertIsNotNone(response)
        self.assertEqual(response.data["other_field"], "Something")
        self.assertNotIn("message", response.data)

    @patch("core.api.exception_handler.drf_exception_handler")
    def test_handle_generic_drf_exception_list_response(self, mock_drf_handler):
        mock_drf_handler.return_value = Response(["Error 1", "Error 2"], status=400)
        exc = APIException("List error")
        response = custom_exception_handler(exc, {})
        self.assertIsNotNone(response)
        self.assertEqual(response.data["message"], ["Error 1", "Error 2"])

    @patch("core.api.exception_handler.drf_exception_handler")
    def test_handle_generic_drf_exception_unknown_data_type(self, mock_drf_handler):
        mock_drf_handler.return_value = Response("String error", status=500)
        exc = APIException("String error")
        response = custom_exception_handler(exc, {})
        self.assertIsNotNone(response)
        self.assertEqual(response.data, "String error")

    def test_unhandled_exception_returns_none(self):
        exc = ZeroDivisionError("Crash")
        response = custom_exception_handler(exc, {})
        self.assertIsNone(response)
