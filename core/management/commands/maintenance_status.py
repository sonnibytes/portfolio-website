import os
from django.core.management.base import BaseCommand
from django.conf import settings
from datetime import datetime


class Command(BaseCommand):
    help = "Check AURA system maintenance mode status"

    def handle(self, *args, **options):
        maintenance_file = os.path.join(settings.BASE_DIR, "MAINTENANCE_MODE")

        if os.path.exists(maintenance_file):
            with open(maintenance_file, "r") as f:
                content = f.read()

            self.stdout.write(
                self.style.WARNING(
                    f"🛠️  MAINTENANCE MODE: ACTIVE\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"{content}"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ MAINTENANCE MODE: DISABLED\n"
                    f"   All AURA systems operational\n"
                    f"   Status checked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
            )
