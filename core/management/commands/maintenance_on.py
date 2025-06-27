import os
from django.core.management.base import BaseCommand
from django.conf import settings
from datetime import datetime


class Command(BaseCommand):
    help = 'Enable AURA system maintenance mode'

    def add_arguments(self, parser):
        parser.add_argument(
            '--message',
            type=str,
            default='Scheduled system maintenance in progress',
            help='Custom maintenance message'
        )
        parser.add_argument(
            '--duration',
            type=str,
            default='2 hours',
            help='Estimated maintenance duration'
        )
    
    def handle(self, *args, **options):
        maintenance_file = os.path.join(settings.BASE_DIR, "MAINTENANCE_MODE")

        maintenance_info = {
            "enabled_at": datetime.now().isoformat(),
            "message": options["message"],
            "duration": options["duration"],
            "enabled_by": "management_command",
        }

        with open(maintenance_file, "w") as f:
            f.write(f"AURA MAINTENANCE MODE ACTIVE\n")
            f.write(f"Enabled: {maintenance_info['enabled_at']}\n")
            f.write(f"Message: {maintenance_info['message']}\n")
            f.write(f"Duration: {maintenance_info['duration']}\n")
            f.write(f"Enabled by: {maintenance_info['enabled_by']}\n")

        self.stdout.write(
            self.style.WARNING(
                f"🛠️  AURA MAINTENANCE MODE ENABLED\n"
                f"   Message: {options['message']}\n"
                f"   Duration: {options['duration']}\n"
                f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        )
