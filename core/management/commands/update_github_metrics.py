"""
Management command to manually update all the summary metrics for existing weekly data,
in case want to update all the repos that already have weekly data but still have old estimated summary metrics.
"""

from django.core.management.base import BaseCommand
from projects.models import GitHubRepository


class Command(BaseCommand):
    help = "Update GitHub repository summary metrics from accurate weekly data"

    def add_arguments(self, parser):
        parser.add_argument(
            '--show-comparison',
            action='store_true',
            help='Show comparison between old estimates and new accurate data',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )
    
    def handle(self, *args, **options):
        show_comparison = options.get('show_comparison', False)
        dry_run = options.get('dry_run', False)

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No changes will be made")
            )
        
        # Get all repos with weekly tracking data
        repos_with_weekly_data = GitHubRepository.objects.filter(
            enable_detailed_tracking=True,
            commit_weeks__isnull=False
        ).distinct()

        if not repos_with_weekly_data:
            self.stdout.write(
                self.style.WARNING('No repositories found with weekly tracking data')
            )
            return
        
        self.stdout.write(
            f'Found {repos_with_weekly_data.count()} repos with weekly data...'
        )

        updated_count = 0

        for repo in repos_with_weekly_data:
            # Show comparison if requested
            if show_comparison:
                comparison = repo.get_accurate_vs_estimated_comparison()
                if comparison:
                    self.stdout.write(f"\n📊 {repo.name}:")
                    self.stdout.write(
                        f"  Estimated: {comparison['estimated']['total']} total, {comparison['estimated']['last_30_days']} recent"
                    )
                    self.stdout.write(
                        f"  Accurate:  {comparison['accurate']['total']} total, {comparison['accurate']['last_30_days']} recent"
                    )

                    total_diff = comparison["difference"]["total"]
                    recent_diff = comparison["difference"]["last_30_days"]

                    if total_diff != 0 or recent_diff != 0:
                        self.stdout.write(
                            f"  Difference: {total_diff:+d} total, {recent_diff:+d} recent"
                        )
                    else:
                        self.stdout.write("  ✓ Already accurate!")

            # Update metrics (unless dry run)
            if not dry_run:
                updated = repo.update_summary_from_weekly_data()
                if updated:
                    updated_count += 1
                    self.stdout.write(f"  ✅ Updated: {repo.name}")
                else:
                    self.stdout.write(f"  ⚠️  Skipped: {repo.name} (no weekly data)")
            else:
                # Dry run - just show what would be updated
                weekly_count = repo.commit_weeks.count()
                if weekly_count > 0:
                    self.stdout.write(
                        f"  Would update: {repo.name} ({weekly_count} weeks of data)"
                    )
                    updated_count += 1
                else:
                    self.stdout.write(f"  Would skip: {repo.name} (no weekly data)")

        # Summary
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nDry run complete: Would update {updated_count} repositories"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nUpdate complete: {updated_count} repositories updated with accurate metrics"
                )
            )

            if updated_count > 0:
                self.stdout.write(
                    "\n💡 Tip: Visit your GitHub integration page to see the updated metrics!"
                )
