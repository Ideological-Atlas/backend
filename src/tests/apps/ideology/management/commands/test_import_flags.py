import shutil
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase, override_settings
from ideology.factories import IdeologyFactory


class ImportFlagsCommandTestCase(TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.mkdtemp()
        self.base_directory = Path(self.temporary_directory) / "src"
        self.fixtures_directory = (
            Path(self.temporary_directory) / "apps" / "ideology" / "fixtures" / "flags"
        )
        self.fixtures_directory.mkdir(parents=True, exist_ok=True)
        self.ideology = IdeologyFactory()
        self.valid_image_bytes = b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
        self.standard_output = StringIO()
        self.standard_error = StringIO()

    def tearDown(self):
        shutil.rmtree(self.temporary_directory)

    def test_import_flags_success(self):
        flag_file_path = self.fixtures_directory / f"{self.ideology.uuid.hex}.png"
        with open(flag_file_path, "wb") as file_handle:
            file_handle.write(self.valid_image_bytes)

        with override_settings(BASE_DIR=str(self.base_directory)):
            call_command(
                "import_flags", stdout=self.standard_output, stderr=self.standard_error
            )

        self.ideology.refresh_from_db()
        self.assertTrue(bool(self.ideology.flag))
        self.assertIn("Updated flag for", self.standard_output.getvalue())

    def test_import_flags_skips_directories(self):
        subdirectory_path = self.fixtures_directory / "subdir"
        subdirectory_path.mkdir()

        with override_settings(BASE_DIR=str(self.base_directory)):
            call_command(
                "import_flags", stdout=self.standard_output, stderr=self.standard_error
            )

        self.assertEqual(self.standard_error.getvalue(), "")

    def test_import_flags_directory_not_found(self):
        empty_directory = Path(tempfile.mkdtemp())
        try:
            with override_settings(BASE_DIR=str(empty_directory / "src")):
                call_command(
                    "import_flags",
                    stdout=self.standard_output,
                    stderr=self.standard_error,
                )
            self.assertIn("Directory not found", self.standard_error.getvalue())
        finally:
            shutil.rmtree(empty_directory)

    def test_import_flags_ideology_not_found(self):
        random_uuid = "00000000000000000000000000000000"
        flag_file_path = self.fixtures_directory / f"{random_uuid}.png"
        with open(flag_file_path, "wb") as file_handle:
            file_handle.write(self.valid_image_bytes)

        with override_settings(BASE_DIR=str(self.base_directory)):
            call_command(
                "import_flags", stdout=self.standard_output, stderr=self.standard_error
            )

        self.assertIn("No Ideology found for UUID", self.standard_output.getvalue())

    @patch("ideology.models.Ideology.objects.get")
    def test_import_flags_generic_error(self, mock_get):
        mock_get.side_effect = Exception("Database Critical Error")

        flag_file_path = self.fixtures_directory / f"{self.ideology.uuid.hex}.png"
        with open(flag_file_path, "wb") as file_handle:
            file_handle.write(self.valid_image_bytes)

        with override_settings(BASE_DIR=str(self.base_directory)):
            call_command(
                "import_flags", stdout=self.standard_output, stderr=self.standard_error
            )

        self.assertIn("Error processing", self.standard_output.getvalue())
