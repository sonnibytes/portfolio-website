# Command to generate learning analytics reports

from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import date, timedelta
import json

from core.models import LearningJourneyManager, PortfolioAnalytics
from projects.models import SystemModule, LearningMilestone
from blog.models import Post


class Command(BaseCommand):
    help = "Generate learning analytics reports"

    def add_arguments(self, parser):
        parser.add_argument(
            "--format",
            choices=["json", "markdown", "console"],
            default="console",
            help="Output format for the report",
        )
        parser.add_argument(
            "--period",
            type=int,
            default=30,
            help="Period in days for analytics (default: 30)",
        )

    def handle(self, *args, **options):
        period = options["period"]
        output_format = options["format"]

        # Generate comprehensive analytics
        analytics_data = self.generate_analytics(period)

        if output_format == "json":
            self.output_json(analytics_data)
        elif output_format == "markdown":
            self.output_markdown(analytics_data)
        else:
            self.output_console(analytics_data)

    def generate_analytics(self, period):
        """Generate comprehensive learning analytics"""
        journey_manager = LearningJourneyManager()

        return {
            "period_days": period,
            "generated_date": timezone.now().isoformat(),
            "learning_overview": journey_manager.get_journey_overview(),
            "skill_progression": journey_manager.get_skill_progression(),
            "learning_timeline": journey_manager.get_learning_timeline(),
            "portfolio_analytics": PortfolioAnalytics.get_learning_summary(period),
            "system_stats": {
                "total_systems": SystemModule.objects.count(),
                "portfolio_ready": SystemModule.objects.filter(
                    portfolio_ready=True
                ).count(),
                "in_development": SystemModule.objects.filter(
                    status="in_development"
                ).count(),
                "learning_stages": self.get_learning_stage_distribution(),
            },
            "content_stats": {
                "total_datalogs": Post.objects.filter(status="published").count(),
                "recent_datalogs": Post.objects.filter(
                    status="published",
                    published_date__gte=timezone.now() - timedelta(days=period),
                ).count(),
                "total_milestones": LearningMilestone.objects.count(),
                "recent_milestones": LearningMilestone.objects.filter(
                    date_achieved__gte=timezone.now() - timedelta(days=period)
                ).count(),
            },
        }

    def get_learning_stage_distribution(self):
        """Get distribution of systems by learning stage"""
        stages = {}
        for choice in SystemModule.LEARNING_STAGE_CHOICES:
            stage_key, stage_label = choice
            count = SystemModule.objects.filter(learning_stage=stage_key).count()
            stages[stage_label] = count
        return stages

    def output_console(self, data):
        """Output analytics to console in readable format"""
        self.stdout.write(self.style.SUCCESS("=== LEARNING JOURNEY ANALYTICS ===\n"))

        overview = data["learning_overview"]
        self.stdout.write(f"Learning Duration: {overview['duration_years']}")
        self.stdout.write(f"Total Learning Hours: {overview['learning_hours']}")
        self.stdout.write(f"Courses Completed: {overview['courses_completed']}")
        self.stdout.write(f"Certificates Earned: {overview['certificates_earned']}")
        self.stdout.write(f"Systems Built: {overview['systems_built']}")
        self.stdout.write(f"Skills Mastered: {overview['skills_mastered']}")

        self.stdout.write(self.style.SUCCESS("\n=== RECENT ACTIVITY ===\n"))
        analytics = data["portfolio_analytics"]
        self.stdout.write(
            f"Learning Hours ({data['period_days']} days): {analytics['total_learning_hours']}"
        )
        self.stdout.write(
            f"DataLog Entries Written: {analytics['total_entries_written']}"
        )
        self.stdout.write(f"Skills Practiced: {analytics['total_skills_practiced']}")
        self.stdout.write(f"Learning Consistency: {analytics['consistency_rate']:.1f}%")

        self.stdout.write(self.style.SUCCESS("\n=== SYSTEM DISTRIBUTION ===\n"))
        system_stats = data["system_stats"]
        for stage, count in system_stats["learning_stages"].items():
            self.stdout.write(f"{stage}: {count} systems")

    def output_json(self, data):
        """Output analytics as JSON"""
        self.stdout.write(json.dumps(data, indent=2, default=str))

    def output_markdown(self, data):
        """Output analytics as Markdown report"""
        # This would render a markdown template
        self.stdout.write("# Learning Journey Analytics Report\n")
        self.stdout.write(f"*Generated: {data['generated_date']}*\n")
        # Add more markdown formatting...
