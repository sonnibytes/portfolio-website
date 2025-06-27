import os
from django.core.management.base import BaseCommand
from django.conf import settings
from datetime import datetime


class Command(BaseCommand):
    help = 'Disable AURA system maintenance mode'

    def handle(self, *args, **options):
        maintenance_file = os.path.join(settings.BASE_DIR, "MAINTENANCE_MODE")

        if os.path.exists(maintenance_file):
            # Read maintenance info before removing
            with open(maintenance_file, "r") as f:
                content = f.read()

            os.remove(maintenance_file)

            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ AURA MAINTENANCE MODE DISABLED\n"
                    f"   System restored: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"   All services operational"
                )
            )
        else:
            self.stdout.write(self.style.WARNING("⚠️  Maintenance mode was not active"))
