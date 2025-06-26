# Management command to sync and maintain learning journey data
# core/management/commands/sync_learning_data.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count, Sum, Avg
from datetime import date, timedelta
import random

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
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Number of days to process for analytics (default: 30)",
        )

    def handle(self, *args, **options):
        if options["update_analytics"]:
            self.update_portfolio_analytics(options["days"])

        if options["sync_skills"]:
            self.sync_skill_relationships()

        if options["calculate_metrics"]:
            self.calculate_learning_metrics()

        if not any(
            [
                options["update_analytics"],
                options["sync_skills"],
                options["calculate_metrics"],
            ]
        ):
            # Run all if no specific option
            self.stdout.write(self.style.SUCCESS("Running all sync operations..."))
            self.update_portfolio_analytics(options["days"])
            self.sync_skill_relationships()
            self.calculate_learning_metrics()

    def update_portfolio_analytics(self, days):
        """Update portfolio analytics with learning data"""
        self.stdout.write(f"Updating portfolio analytics for last {days} days...")

        created_count = 0
        updated_count = 0

        # Get or create analytics for recent days
        for i in range(days):
            analytics_date = date.today() - timedelta(days=i)
            analytics, created = PortfolioAnalytics.objects.get_or_create(
                date=analytics_date,
                defaults={
                    "learning_hours_logged": 0.0,
                    "datalog_entries_written": 0,
                    "skills_practiced": 0,
                    "projects_worked_on": 0,
                    "milestones_achieved": 0,
                },
            )

            if created:
                created_count += 1
                # Calculate estimated learning data for this date
                analytics.learning_hours_logged = self.estimate_daily_learning_hours(
                    analytics_date
                )
                analytics.datalog_entries_written = Post.objects.filter(
                    status="published", published_date__date=analytics_date
                ).count()
                analytics.projects_worked_on = SystemModule.objects.filter(
                    updated_at__date=analytics_date
                ).count()
                analytics.milestones_achieved = LearningMilestone.objects.filter(
                    date_achieved__date=analytics_date
                ).count()

                # Calculate skills practiced (estimate based on project work)
                if analytics.projects_worked_on > 0:
                    analytics.skills_practiced = random.randint(2, 5)
                elif analytics.learning_hours_logged > 1:
                    analytics.skills_practiced = random.randint(1, 3)

                analytics.save()
            else:
                # Update existing analytics if needed
                if (
                    analytics.learning_hours_logged == 0
                    and analytics.projects_worked_on == 0
                ):
                    analytics.learning_hours_logged = (
                        self.estimate_daily_learning_hours(analytics_date)
                    )
                    analytics.save()
                    updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Portfolio analytics updated: {created_count} created, {updated_count} updated"
            )
        )

    def sync_skill_relationships(self):
        """Sync skills between education and projects"""
        self.stdout.write("Syncing skill relationships...")

        connections_made = 0
        categories_synced = 0

        # Auto-connect skills to technologies where names match
        for skill in Skill.objects.all():
            if (
                not hasattr(skill, "related_technology")
                or skill.related_technology is None
            ):
                matching_tech = Technology.objects.filter(
                    name__iexact=skill.name
                ).first()
                if matching_tech:
                    skill.related_technology = matching_tech
                    skill.save()
                    connections_made += 1
                    self.stdout.write(
                        f"  Connected {skill.name} to {matching_tech.name}"
                    )

        # NEW ENHANCEMENT: Sync categories from related technologies to skills
        for skill in Skill.objects.filter(related_technology__isnull=False):
            # Check if skill needs category update
            should_update_category = (
                not skill.category  # No category set
                or skill.category == "other"  # Default/generic category
            )

            if should_update_category and skill.related_technology.category:
                # Map technology categories to skill categories
                tech_to_skill_category_map = {
                    "language": "language",
                    "framework": "framework",
                    "database": "database",
                    "cloud": "tool",  # Cloud services mapped to tools
                    "tool": "tool",
                    "other": "other",
                }

                tech_category = skill.related_technology.category
                new_skill_category = tech_to_skill_category_map.get(
                    tech_category, "other"
                )

                if new_skill_category != skill.category:
                    old_category = (
                        skill.get_category_display() if skill.category else "None"
                    )
                    skill.category = new_skill_category
                    skill.save()
                    categories_synced += 1
                    self.stdout.write(
                        f"  Updated {skill.name} category: {old_category} → {skill.get_category_display()}"
                    )

        # Auto-create education-skill relationships for programming courses
        education_skills_created = 0
        programming_education = Education.objects.filter(
            learning_type__in=["online_course", "certification"],
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
                    education_skills_created += 1
                    self.stdout.write(f"  Connected {skill.name} to {edu.degree}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Skill relationships synced: {connections_made} tech connections, "
                f"{categories_synced} categories synced, "
                f"{education_skills_created} education-skill connections"
            )
        )

    def calculate_learning_metrics(self):
        """Recalculate all learning metrics"""
        self.stdout.write("Calculating learning metrics...")

        skills_updated = 0
        systems_updated = 0

        # Update skill proficiency based on project usage
        for skill in Skill.objects.all():
            skill_gains = SystemSkillGain.objects.filter(skill=skill)
            if skill_gains.exists():
                # Calculate average proficiency from projects
                total_proficiency = sum(
                    [gain.proficiency_gained for gain in skill_gains]
                )
                avg_proficiency = total_proficiency / skill_gains.count()

                # Update skill proficiency if not manually set (only update basic skills)
                if skill.proficiency <= 2:
                    new_proficiency = min(
                        5, max(skill.proficiency, int(avg_proficiency))
                    )
                    if new_proficiency != skill.proficiency:
                        skill.proficiency = new_proficiency
                        skill.save()
                        skills_updated += 1
                        self.stdout.write(
                            f"  Updated {skill.name} proficiency to {new_proficiency}"
                        )

        # Update system portfolio readiness
        for system in SystemModule.objects.all():
            try:
                readiness_score = system.get_portfolio_readiness_score()
                if readiness_score >= 70 and not system.portfolio_ready:
                    system.portfolio_ready = True
                    system.save()
                    systems_updated += 1
                    self.stdout.write(
                        f"  Marked {system.title} as portfolio ready (score: {readiness_score})"
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f"  Could not calculate readiness for {system.title}: {e}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Learning metrics calculated: {skills_updated} skills updated, "
                f"{systems_updated} systems marked portfolio-ready"
            )
        )

    def get_relevant_skills_for_education(self, education):
        """Get relevant skills based on education content"""
        relevant_skills = []

        # Keywords mapping to skills
        keyword_skill_map = {
            "python": "Python",
            "django": "Django",
            "javascript": "JavaScript",
            "react": "React",
            "html": "HTML",
            "css": "CSS",
            "sql": "SQL",
            "postgresql": "PostgreSQL",
            "git": "Git",
            "github": "GitHub",
            "linux": "Linux",
            "docker": "Docker",
            "api": "REST API",
            "bootstrap": "Bootstrap",
            "jquery": "jQuery",
            "node": "Node.js",
            "express": "Express.js",
            "mongodb": "MongoDB",
            "mysql": "MySQL",
            "aws": "AWS",
            "azure": "Azure",
            "gcp": "Google Cloud",
        }

        # Check course title and description for relevant keywords
        text_to_search = f"{education.degree} {education.description}".lower()

        for keyword, skill_name in keyword_skill_map.items():
            if keyword in text_to_search:
                try:
                    skill = Skill.objects.get(name__iexact=skill_name)
                    relevant_skills.append(skill)
                except Skill.DoesNotExist:
                    continue

        return relevant_skills

    def estimate_daily_learning_hours(self, date_obj):
        """Estimate learning hours for a given date (placeholder for real tracking)"""
        # This would be replaced with real data in production
        # For now, generate realistic estimates based on day of week
        weekday = date_obj.weekday()

        # Weekend days typically have more learning time
        if weekday in [5, 6]:  # Saturday, Sunday
            return round(random.uniform(2.0, 6.0), 1)
        else:  # Weekdays
            return round(random.uniform(1.0, 4.0), 1)

    def calculate_portfolio_summary(self):
        """Calculate and display portfolio summary"""
        total_systems = SystemModule.objects.count()
        portfolio_ready = SystemModule.objects.filter(portfolio_ready=True).count()
        total_skills = Skill.objects.count()
        mastered_skills = Skill.objects.filter(proficiency__gte=4).count()
        total_education = Education.objects.count()
        total_milestones = LearningMilestone.objects.count()

        self.stdout.write(self.style.SUCCESS("\n=== PORTFOLIO SUMMARY ==="))
        self.stdout.write(
            f"Systems: {total_systems} total, {portfolio_ready} portfolio-ready"
        )
        self.stdout.write(f"Skills: {total_skills} total, {mastered_skills} mastered")
        self.stdout.write(f"Education: {total_education} entries")
        self.stdout.write(f"Milestones: {total_milestones} achievements")

        # Recent analytics
        recent_analytics = PortfolioAnalytics.objects.filter(
            date__gte=date.today() - timedelta(days=30)
        )
        total_hours = (
            recent_analytics.aggregate(Sum("learning_hours_logged"))[
                "learning_hours_logged__sum"
            ]
            or 0
        )
        self.stdout.write(f"Learning hours (30 days): {total_hours:.1f}")

    def show_learning_recommendations(self):
        """Show recommendations for improving learning data"""
        recommendations = []

        # Check for systems without skills
        systems_without_skills = SystemModule.objects.annotate(
            skills_count=Count("skills_developed")
        ).filter(skills_count=0)

        if systems_without_skills.exists():
            recommendations.append(
                f"Add skill connections to {systems_without_skills.count()} systems"
            )

        # Check for skills without education sources
        skills_without_education = Skill.objects.annotate(
            education_count=Count("learned_through_education")
        ).filter(education_count=0)

        if skills_without_education.exists():
            recommendations.append(
                f"Add education sources to {skills_without_education.count()} skills"
            )

        # Check for recent systems without milestones
        recent_systems = (
            SystemModule.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=90)
            )
            .annotate(milestones_count=Count("milestones"))
            .filter(milestones_count=0)
        )

        if recent_systems.exists():
            recommendations.append(
                f"Add milestones to {recent_systems.count()} recent systems"
            )

        if recommendations:
            self.stdout.write(self.style.WARNING("\n=== RECOMMENDATIONS ==="))
            for rec in recommendations:
                self.stdout.write(f"• {rec}")
        else:
            self.stdout.write(self.style.SUCCESS("\n✅ Learning data looks complete!"))