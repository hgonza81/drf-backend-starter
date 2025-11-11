"""
Management command to seed the entire database with sample data for development
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = "Seed database with sample data for development"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before seeding",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting database seeding..."))

        self._validate_arguments(options)

        try:
            with transaction.atomic():
                if options["clear"]:
                    self._clear_data()

                # Seed in dependency order

            self.stdout.write(
                self.style.SUCCESS("Database seeding completed successfully!")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during seeding: {str(e)}"))
            raise CommandError(f"Seeding failed: {str(e)}") from e

    def _validate_arguments(self, options):
        # raise CommandError("Raise an error if the argument is invalid")
        pass

    def _clear_data(self):
        self.stdout.write("Clearing existing data...")

        try:
            # Clear in reverse dependency order to avoid foreign key constraints

            self.stdout.write(
                self.style.WARNING("✓ Cleared existing data (kept superusers and )")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error clearing data: {str(e)}"))
            raise
