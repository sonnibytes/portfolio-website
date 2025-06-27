from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
from django.core.cache import cache
import os
import sys
from datetime import datetime


class Command(BaseCommand):
    help = "Perform AURA system health check"

    def add_arguments(self, parser):
        parser.add_argument(
            "--verbose", action="store_true", help="Show detailed health check results"
        )

    def handle(self, *args, **options):
        verbose = options["verbose"]

        self.stdout.write(
            self.style.HTTP_INFO(
                f"🔍 AURA SYSTEM HEALTH CHECK\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
            )
        )

        health_status = {
            "database": self.check_database(verbose),
            "cache": self.check_cache(verbose),
            "static_files": self.check_static_files(verbose),
            "templates": self.check_templates(verbose),
            "maintenance_mode": self.check_maintenance_mode(verbose),
        }

        # Overall status
        all_healthy = all(health_status.values())

        if all_healthy:
            self.stdout.write(
                self.style.SUCCESS(
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"✅ OVERALL STATUS: ALL SYSTEMS OPERATIONAL\n"
                    f"   AURA portfolio ready for deployment"
                )
            )
        else:
            failed_systems = [k for k, v in health_status.items() if not v]
            self.stdout.write(
                self.style.ERROR(
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"❌ OVERALL STATUS: ISSUES DETECTED\n"
                    f"   Failed systems: {', '.join(failed_systems)}"
                )
            )

    def check_database(self, verbose):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()

            if verbose:
                self.stdout.write("📊 Database: ✅ Connected and responsive")
            return True
        except Exception as e:
            if verbose:
                self.stdout.write(f"📊 Database: ❌ Connection failed - {e}")
            return False

    def check_cache(self, verbose):
        try:
            cache.set("health_check", "test", 30)
            result = cache.get("health_check")

            if result == "test":
                if verbose:
                    self.stdout.write("💾 Cache: ✅ Read/write operations successful")
                return True
            else:
                if verbose:
                    self.stdout.write("💾 Cache: ❌ Read/write test failed")
                return False
        except Exception as e:
            if verbose:
                self.stdout.write(f"💾 Cache: ❌ Cache system error - {e}")
            return False

    def check_static_files(self, verbose):
        try:
            static_root = getattr(settings, "STATIC_ROOT", None)
            static_dirs = getattr(settings, "STATICFILES_DIRS", [])

            if static_root and os.path.exists(static_root):
                static_files_exist = True
            elif static_dirs and any(os.path.exists(d) for d in static_dirs):
                static_files_exist = True
            else:
                static_files_exist = False

            if static_files_exist:
                if verbose:
                    self.stdout.write("🎨 Static Files: ✅ Directories accessible")
                return True
            else:
                if verbose:
                    self.stdout.write(
                        "🎨 Static Files: ❌ Static directories not found"
                    )
                return False
        except Exception as e:
            if verbose:
                self.stdout.write(f"🎨 Static Files: ❌ Static files error - {e}")
            return False

    def check_templates(self, verbose):
        try:
            from django.template.loader import get_template

            critical_templates = ["404.html", "500.html", "403.html"]
            missing_templates = []

            for template_name in critical_templates:
                try:
                    get_template(template_name)
                except:
                    missing_templates.append(template_name)

            if not missing_templates:
                if verbose:
                    self.stdout.write("📄 Templates: ✅ All error templates found")
                return True
            else:
                if verbose:
                    self.stdout.write(
                        f"📄 Templates: ❌ Missing: {', '.join(missing_templates)}"
                    )
                return False
        except Exception as e:
            if verbose:
                self.stdout.write(f"📄 Templates: ❌ Template system error - {e}")
            return False

    def check_maintenance_mode(self, verbose):
        maintenance_file = os.path.join(settings.BASE_DIR, "MAINTENANCE_MODE")

        if os.path.exists(maintenance_file):
            if verbose:
                self.stdout.write("🛠️  Maintenance: ⚠️  Maintenance mode is ACTIVE")
            return True  # This is actually "healthy" if maintenance is intentional
        else:
            if verbose:
                self.stdout.write("🛠️  Maintenance: ✅ Normal operations mode")
            return True
