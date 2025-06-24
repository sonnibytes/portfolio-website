# Management command to sync and maintain learning journey data

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from django.db.models import Count, Sum

from core.models import Education, Skill, PortfolioAnalytics, EducationSkillDevelopment
from projects.models import SystemModule, SystemSkillGain, LearningMilestone, Technology
from blog.models import Post


class Command(BaseCommand):
    help = "Sync and maintain learning journey data relationships"

    def add_arguments(self, parser):
        parser.add_argument(
            "--update-analytics",
            action="store_true",
            help="Update portfolio analytics for recent days",
        )
        parser.add_argument(
            "--sync-skills",
            action="store_true",
            help="Sync skills between education and projects",
        )
        parser.add_argument(
            "--calculate-metrics",
            action="store_true",
            help="Recalculate all learning metrics",
        )

    def handle(self, *args, **options):
        if options["update_analytics"]:
            self.update_portfolio_analytics()

        if options["sync_skills"]:
            self.sync_skill_relationships()

        if options["calculate_metrics"]:
            self.calculate_learning_metrics()

        if not any(options.values()):
            # Run all if no specific option
            self.update_portfolio_analytics()
            self.sync_skill_relationships()
            self.calculate_learning_metrics()

    def update_portfolio_analytics(self):
        """Update portfolio analytics with learning data"""
        self.stdout.write("Updating portfolio analytics...")

        # Get or create analytics for recent days
        for i in range(30):  # Last 30 days
            analytics_date = date.today() - timedelta(days=i)
            analytics, created = PortfolioAnalytics.objects.get_or_create(
                date=analytics_date,
                defaults={
                    "learning_hours_logged": 0.0,
                    "datalog_entries_written": 0,
                    "skills_practiced": 0,
                    "projects_worked_on": 0,
                },
            )

            if created:
                # Calculate estimated learning data for this date
                # TODO: (This would be populated by real tracking in production)
                analytics.learning_hours_logged = self.estimate_daily_learning_hours(
                    analytics_date
                )
                analytics.datalog_entries_written = Post.objects.filter(
                    status="published", published_date__date=analytics_date
                ).count()
                analytics.projects_worked_on = SystemModule.objects.filter(
                    updated_at__date=analytics_date
                ).count()
                analytics.save()

        self.stdout.write(self.style.SUCCESS("Portfolio analytics updated"))

    def sync_skill_relationships(self):
        """Sync skills between education and projects"""
        self.stdout.write("Syncing skill relationships...")

        # Auto-connect skills to technologies where names match
        for skill in Skill.objects.all():
            matching_tech = Technology.objects.filter(name__iexact=skill.name).first()
            if matching_tech and not hasattr(skill, "related_technology"):
                skill.related_technology = matching_tech
                skill.save()
                self.stdout.write(f"Connected {skill.name} to {matching_tech.name}")

        # Auto-create education-skill relationships for programming courses
        programming_education = Education.objects.filter(
            learning_type__in=["online_course", "certification"],
            field_of_study__icontains="programming",
        )

        for edu in programming_education:
            # Auto-assign relevant skills based on course title/description
            relevant_skills = self.get_relevant_skills_for_education(edu)
            for skill in relevant_skills:
                relationship, created = EducationSkillDevelopment.objects.get_or_create(
                    education=edu,
                    skill=skill,
                    defaults={
                        "proficiency_before": 0,
                        "proficiency_after": 3,
                        "learning_focus": "foundation",
                        "importance_in_curriculum": 3,
                    },
                )
                if created:
                    self.stdout.write(f"Connected {skill.name} to {edu.degree}")

        self.stdout.write(self.style.SUCCESS("Skill relationships synced"))

    def calculate_learning_metrics(self):
        """Recalculate all learning metrics"""
        self.stdout.write("Calculating learning metrics...")

        # Update skill proficiency based on project usage
        for skill in Skill.objects.all():
            skill_gains = SystemSkillGain.objects.filter(skill=skill)
            if skill_gains.exists():
                # Calculate average proficiency from projects
                avg_proficiency = skill_gains.aggregate(
                    avg=Sum("proficiency_gained") / Count("id")
                )["avg"]

                # Update skill proficiency if not manually set
                if skill.proficiency <= 2:  # Only update basic skills
                    skill.proficiency = min(
                        5, max(skill.proficiency, int(avg_proficiency))
                    )
                    skill.save()

        # Update system portfolio readiness
        for system in SystemModule.objects.all():
            readiness_score = system.get_portfolio_readiness_score()
            if readiness_score >= 70 and not system.portfolio_ready:
                system.portfolio_ready = True
                system.save()
                self.stdout.write(f"Marked {system.title} as portfolio ready")

        self.stdout.write(self.style.SUCCESS("Learning metrics calculated"))

    def get_relevant_skills_for_education(self, education):
        """Get relevant skills based on education content"""
        relevant_skills = []

        # Keywords mapping to skills
        keyword_skill_map = {
            "python": "Python",
            "django": "Django",
            "javascript": "JavaScript",
            "html": "HTML/CSS",
            "css": "HTML/CSS",
            "git": "Git/GitHub",
            "sql": "SQL",
            "database": "Database Design",
            "api": "API Development",
            "web": "Web Development",
        }

        content_text = f"{education.degree} {education.description} {education.field_of_study}".lower()

        for keyword, skill_name in keyword_skill_map.items():
            if keyword in content_text:
                skill = Skill.objects.filter(name__icontains=skill_name).first()
                if skill and skill not in relevant_skills:
                    relevant_skills.append(skill)

        return relevant_skills[:5]  # Limit to 5 most relevant

    def estimate_daily_learning_hours(self, date):
        """ TODO: Estimate learning hours for a given date (placeholder for real tracking)"""
        import random

        # This would be replaced with real data in production
        # For now, generate realistic estimates
        weekday = date.weekday()
        if weekday < 5:  # Weekdays
            return round(random.uniform(1.5, 4.0), 1)
        else:  # Weekends
            return round(random.uniform(2.0, 6.0), 1)
