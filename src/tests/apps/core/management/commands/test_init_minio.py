from io import StringIO
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.test import TestCase


class InitMinioCommandTestCase(TestCase):
    def call_command(self, *args, **kwargs):
        out = StringIO()
        kwargs["stdout"] = out
        call_command("init_minio", *args, **kwargs)
        return out.getvalue()

    @patch("core.management.commands.init_minio.boto3.resource")
    def test_init_minio_success(self, mock_boto):
        mock_s3 = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.creation_date = None
        mock_boto.return_value = mock_s3
        mock_s3.Bucket.return_value = mock_bucket

        output = self.call_command()
        mock_bucket.create.assert_called_once()
        self.assertIn("Public policy applied", output)

    @patch("core.management.commands.init_minio.boto3.resource")
    def test_init_minio_bucket_exists(self, mock_boto):
        mock_s3 = MagicMock()
        mock_bucket = MagicMock()
        mock_bucket.creation_date = "2024-01-01"
        mock_boto.return_value = mock_s3
        mock_s3.Bucket.return_value = mock_bucket

        self.call_command()
        mock_bucket.create.assert_not_called()

    @patch("django.conf.settings.AWS_S3_ENDPOINT_URL", None)
    def test_init_minio_no_url(self):
        output = self.call_command()
        self.assertIn("S3 Endpoint not configured", output)

    @patch("core.management.commands.init_minio.boto3.resource")
    def test_init_minio_exception(self, mock_boto):
        mock_boto.side_effect = Exception("Connection error")
        output = self.call_command()
        self.assertIn("MinIO Error: Connection error", output)
