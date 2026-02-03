from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from ideology.models import Ideology


class Command(BaseCommand):
    help = "Imports flags from fixtures/flags matching filename UUID to Ideology UUID."

    def handle(self, *args, **options):
        fixtures_dir = (
            Path(settings.BASE_DIR).parent / "apps" / "ideology" / "fixtures" / "flags"
        )

        if not fixtures_dir.exists():
            self.stderr.write(self.style.ERROR(f"Directory not found: {fixtures_dir}"))
            return

        self.stdout.write(f"Scanning {fixtures_dir} for flags...")

        files_scanned = 0
        updated_count = 0

        for file_path in fixtures_dir.iterdir():
            if not file_path.is_file():
                continue

            files_scanned += 1
            uuid_hex = file_path.stem

            try:
                ideology = Ideology.objects.get(uuid=uuid_hex)

                with open(file_path, "rb") as f:
                    ideology.flag.save(file_path.name, File(f), save=True)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Updated flag for: {ideology.name} ({uuid_hex})"
                    )
                )
                updated_count += 1

            except Ideology.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"No Ideology found for UUID: {uuid_hex} (File: {file_path.name})"
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error processing {file_path.name}: {e}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Process complete. Scanned {files_scanned} files, updated {updated_count} ideologies."
            )
        )
