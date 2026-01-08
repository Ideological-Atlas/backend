from unittest.mock import Mock, patch

from core.exceptions.api_exceptions import NotFoundException
from django.test import TestCase
from ideology.api.views.base_views import BaseUpsertAnswerView
from rest_framework import serializers, status


class MockSerializer(serializers.Serializer):
    value = serializers.CharField()


class BaseViewCoverageTestCase(TestCase):
    def setUp(self):
        self.view = BaseUpsertAnswerView()
        self.view.request = Mock()
        self.view.request.method = "POST"
        self.view.write_serializer_class = MockSerializer
        self.view.read_serializer_class = MockSerializer
        self.view.format_kwarg = None

    def test_get_serializer_class_logic(self):
        self.view.created_object = Mock()
        self.assertEqual(self.view.get_serializer_class(), MockSerializer)

        self.view.created_object = None
        self.assertEqual(self.view.get_serializer_class(), MockSerializer)

        self.view.write_serializer_class = None
        self.view.serializer_class = MockSerializer
        self.assertEqual(self.view.get_serializer_class(), MockSerializer)

    @patch("ideology.api.views.base_views.BaseUpsertAnswerView.get_serializer")
    def test_create_not_found_exception(self, mock_get_serializer):
        mock_serializer = Mock()
        mock_serializer.is_valid.return_value = True
        mock_serializer.validated_data = {"val": "data"}
        mock_get_serializer.return_value = mock_serializer

        self.view.reference_model = Mock()
        self.view.reference_model.objects.filter.return_value.first.return_value = None
        self.view.reference_model.__name__ = "RefModel"

        self.view.target_model = Mock()
        self.view.request_uuid_key = "uuid"
        self.view.request_value_key = "val"
        self.view.lookup_url_kwarg = "uuid"
        self.view.kwargs = {"uuid": "123"}

        with self.assertRaises(NotFoundException):
            self.view.create(self.view.request)

    def test_create_missing_configuration(self):
        with self.assertRaises(NotImplementedError):
            self.view.create(self.view.request)

    @patch("ideology.api.views.base_views.BaseUpsertAnswerView.get_serializer")
    def test_create_success_flow(self, mock_get_serializer):
        mock_serializer_instance = Mock()
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer_instance.validated_data = {"value": "test_val"}
        mock_serializer_instance.data = {"value": "test_val"}
        mock_get_serializer.return_value = mock_serializer_instance

        mock_ref_obj = Mock()
        self.view.reference_model = Mock()
        self.view.reference_model.objects.filter.return_value.first.return_value = (
            mock_ref_obj
        )

        self.view.target_model = Mock()
        mock_created_obj = Mock()
        self.view.target_model.objects.update_or_create.return_value = (
            mock_created_obj,
            True,
        )

        self.view.reference_field = "ref"
        self.view.request_value_key = "value"
        self.view.target_value_key = "value"
        self.view.lookup_url_kwarg = "uuid"
        self.view.kwargs = {"uuid": "123"}
        self.view.request.user = Mock()

        response = self.view.create(self.view.request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
