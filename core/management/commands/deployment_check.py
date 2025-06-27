from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import call_command
from django.core.checks import run_checks
import os


class Command(BaseCommand):
    help = "Comprehensive AURA deployment readiness check"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.HTTP_INFO(
                f"🚀 AURA DEPLOYMENT READINESS CHECK\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )
        )

        checks_passed = 0
        total_checks = 6

        # 1. Django system checks
        self.stdout.write("\n1️⃣  Running Django system checks...")
        try:
            call_command("check", verbosity=0)
            self.stdout.write(self.style.SUCCESS("   ✅ Django system checks passed"))
            checks_passed += 1
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"   ❌ Django system checks failed: {e}")
            )

        # 2. Database migrations
        self.stdout.write("\n2️⃣  Checking database migrations...")
        try:
            call_command("showmigrations", verbosity=0)
            self.stdout.write(
                self.style.SUCCESS("   ✅ Database migrations status verified")
            )
            checks_passed += 1
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Migration check failed: {e}"))

        # 3. Static files collection
        self.stdout.write("\n3️⃣  Checking static files...")
        if settings.DEBUG:
            self.stdout.write(
                self.style.WARNING(
                    "   ⚠️  DEBUG=True - Run collectstatic before production"
                )
            )
        else:
            if hasattr(settings, "STATIC_ROOT") and os.path.exists(
                settings.STATIC_ROOT
            ):
                self.stdout.write(
                    self.style.SUCCESS("   ✅ Static files collected and ready")
                )
                checks_passed += 1
            else:
                self.stdout.write(
                    self.style.ERROR(
                        "   ❌ Static files not collected - run collectstatic"
                    )
                )

        # 4. Error templates
        self.stdout.write("\n4️⃣  Verifying error page templates...")
        try:
            from django.template.loader import get_template

            error_templates = ["404.html", "500.html", "403.html", "maintenance.html"]
            missing = []

            for template in error_templates:
                try:
                    get_template(template)
                except:
                    missing.append(template)

            if not missing:
                self.stdout.write(
                    self.style.SUCCESS("   ✅ All AURA error templates ready")
                )
                checks_passed += 1
            else:
                self.stdout.write(
                    self.style.ERROR(f"   ❌ Missing templates: {', '.join(missing)}")
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Template check failed: {e}"))

        # 5. Security settings
        self.stdout.write("\n5️⃣  Checking security configuration...")
        security_issues = []

        if settings.DEBUG:
            security_issues.append("DEBUG=True")
        if (
            settings.SECRET_KEY == "your-secret-key-here"
            or len(settings.SECRET_KEY) < 40
        ):
            security_issues.append("Weak SECRET_KEY")
        if not getattr(settings, "ALLOWED_HOSTS", None):
            security_issues.append("ALLOWED_HOSTS not configured")

        if not security_issues:
            self.stdout.write(self.style.SUCCESS("   ✅ Security settings configured"))
            checks_passed += 1
        else:
            self.stdout.write(
                self.style.ERROR(f"   ❌ Security issues: {', '.join(security_issues)}")
            )

        # 6. System health
        self.stdout.write("\n6️⃣  Running system health check...")
        try:
            call_command("system_health", verbosity=0)
            self.stdout.write(self.style.SUCCESS("   ✅ System health verified"))
            checks_passed += 1
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Health check failed: {e}"))

        # Final results
        self.stdout.write(
            f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )

        if checks_passed == total_checks:
            self.stdout.write(
                self.style.SUCCESS(
                    f"🎉 DEPLOYMENT READY!\n"
                    f"   All {total_checks} checks passed\n"
                    f"   AURA portfolio system ready for production"
                )
            )
        else:
            failed = total_checks - checks_passed
            self.stdout.write(
                self.style.ERROR(
                    f"⚠️  DEPLOYMENT ISSUES DETECTED\n"
                    f"   {checks_passed}/{total_checks} checks passed\n"
                    f"   {failed} issue(s) need attention before deployment"
                )
            )
