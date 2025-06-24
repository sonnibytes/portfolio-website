# core/management/commands/check_sample_data.py
# Quick command to see exactly what sample data exists

from django.core.management.base import BaseCommand
from django.db.models import Sum

from core.models import (
    Education,
    Experience,
    Skill,
    PortfolioAnalytics,
    EducationSkillDevelopment,
)
from projects.models import SystemModule, LearningMilestone, Technology
from blog.models import Post


class Command(BaseCommand):
    help = "Check what sample data currently exists"

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("📊 CURRENT SAMPLE DATA STATUS"))
        self.stdout.write("=" * 60)

        # Education
        self.check_education()
        self.stdout.write("")

        # Experience
        self.check_experience()
        self.stdout.write("")

        # Skills
        self.check_skills()
        self.stdout.write("")

        # Systems
        self.check_systems()
        self.stdout.write("")

        # Milestones
        self.check_milestones()
        self.stdout.write("")

        # Connections
        self.check_connections()
        self.stdout.write("")

        # Analytics
        self.check_analytics()

        self.stdout.write("=" * 60)

    def check_education(self):
        """Check education data"""
        education_count = Education.objects.count()
        self.stdout.write(f"📚 EDUCATION: {education_count} entries")

        if education_count > 0:
            completed = Education.objects.filter(end_date__isnull=False).count()
            current = Education.objects.filter(is_current=True).count()
            total_hours = (
                Education.objects.aggregate(total=Sum("hours_completed"))["total"] or 0
            )

            self.stdout.write(f"   ├─ Completed courses: {completed}")
            self.stdout.write(f"   ├─ Current courses: {current}")
            self.stdout.write(f"   └─ Total learning hours: {total_hours}")

            # Show a few examples
            for edu in Education.objects.all()[:3]:
                status = "✅ Complete" if edu.end_date else "🔄 In Progress"
                self.stdout.write(f"     • {edu.degree} ({edu.platform}) {status}")

            if education_count > 3:
                self.stdout.write(f"     ... and {education_count - 3} more")
        else:
            self.stdout.write("   └─ No education entries found")

    def check_experience(self):
        """Check experience data"""
        experience_count = Experience.objects.count()
        self.stdout.write(f"💼 EXPERIENCE: {experience_count} entries")

        if experience_count > 0:
            current = Experience.objects.filter(is_current=True).count()
            self.stdout.write(f"   ├─ Current positions: {current}")
            self.stdout.write(f"   └─ Total positions: {experience_count}")

            for exp in Experience.objects.all():
                status = "🔄 Current" if exp.is_current else "✅ Past"
                self.stdout.write(f"     • {exp.position} at {exp.company} {status}")
        else:
            self.stdout.write("   └─ No experience entries found")

    def check_skills(self):
        """Check skills data"""
        skill_count = Skill.objects.count()
        self.stdout.write(f"🎯 SKILLS: {skill_count} entries")

        if skill_count > 0:
            featured = Skill.objects.filter(is_featured=True).count()
            learning = Skill.objects.filter(is_currently_learning=True).count()
            mastered = Skill.objects.filter(proficiency__gte=4).count()

            self.stdout.write(f"   ├─ Featured skills: {featured}")
            self.stdout.write(f"   ├─ Currently learning: {learning}")
            self.stdout.write(f"   └─ Mastered (4+ proficiency): {mastered}")

            # Show by category
            categories = Skill.objects.values_list("category", flat=True).distinct()
            for category in categories:
                count = Skill.objects.filter(category=category).count()
                category_display = dict(Skill.CATEGORY_CHOICES).get(category, category)
                self.stdout.write(f"     • {category_display}: {count} skills")
        else:
            self.stdout.write("   └─ No skills found")

    def check_systems(self):
        """Check systems/projects data"""
        systems_count = SystemModule.objects.count()
        self.stdout.write(f"🔧 SYSTEMS/PROJECTS: {systems_count} entries")

        if systems_count > 0:
            published = SystemModule.objects.filter(status="published").count()
            in_dev = SystemModule.objects.filter(status="in_development").count()
            portfolio_ready = SystemModule.objects.filter(portfolio_ready=True).count()

            self.stdout.write(f"   ├─ Published: {published}")
            self.stdout.write(f"   ├─ In development: {in_dev}")
            self.stdout.write(f"   └─ Portfolio ready: {portfolio_ready}")

            # Show examples
            for system in SystemModule.objects.all()[:3]:
                ready = "✅ Ready" if system.portfolio_ready else "🔄 In Progress"
                self.stdout.write(f"     • {system.title} ({system.status}) {ready}")

            if systems_count > 3:
                self.stdout.write(f"     ... and {systems_count - 3} more")
        else:
            self.stdout.write("   └─ No systems found")
            self.stdout.write("     ⚠️  This is why no milestones were created!")

    def check_milestones(self):
        """Check learning milestones"""
        milestones_count = LearningMilestone.objects.count()
        self.stdout.write(f"🏆 LEARNING MILESTONES: {milestones_count} entries")

        if milestones_count > 0:
            # Group by milestone type
            milestone_types = LearningMilestone.objects.values_list(
                "milestone_type", flat=True
            ).distinct()
            for milestone_type in milestone_types:
                count = LearningMilestone.objects.filter(
                    milestone_type=milestone_type
                ).count()
                type_display = dict(LearningMilestone.MILESTONE_TYPES).get(
                    milestone_type, milestone_type
                )
                self.stdout.write(f"   ├─ {type_display}: {count}")

            # Show recent milestones
            recent_milestones = LearningMilestone.objects.order_by("-date_achieved")[:3]
            self.stdout.write("   └─ Recent milestones:")
            for milestone in recent_milestones:
                self.stdout.write(
                    f"     • {milestone.title} → {milestone.system.title}"
                )
        else:
            self.stdout.write("   └─ No milestones found")
            if SystemModule.objects.count() == 0:
                self.stdout.write(
                    "     ℹ️  Create SystemModule objects first to enable milestones"
                )

    def check_connections(self):
        """Check education-skill connections"""
        connections_count = EducationSkillDevelopment.objects.count()
        self.stdout.write(
            f"🔗 EDUCATION-SKILL CONNECTIONS: {connections_count} entries"
        )

        if connections_count > 0:
            # Show connections per education
            for edu in Education.objects.all()[:3]:
                skills_count = edu.skills_learned.count()
                self.stdout.write(f"   • {edu.degree}: {skills_count} skills connected")

            total_education = Education.objects.count()
            if total_education > 3:
                self.stdout.write(f"   ... and {total_education - 3} more courses")
        else:
            self.stdout.write("   └─ No education-skill connections found")

    def check_analytics(self):
        """Check portfolio analytics"""
        analytics_count = PortfolioAnalytics.objects.count()
        self.stdout.write(f"📈 PORTFOLIO ANALYTICS: {analytics_count} entries")

        if analytics_count > 0:
            total_hours = (
                PortfolioAnalytics.objects.aggregate(
                    total=Sum("learning_hours_logged")
                )["total"]
                or 0
            )

            recent_days = PortfolioAnalytics.objects.filter(
                learning_hours_logged__gt=0
            ).count()

            latest = PortfolioAnalytics.objects.order_by("-date").first()
            oldest = PortfolioAnalytics.objects.order_by("date").first()

            self.stdout.write(f"   ├─ Total learning hours logged: {total_hours:.1f}")
            self.stdout.write(f"   ├─ Days with learning activity: {recent_days}")
            self.stdout.write(f"   └─ Date range: {oldest.date} to {latest.date}")
        else:
            self.stdout.write("   └─ No analytics entries found")

    def show_next_steps(self):
        """Show what to do next"""
        self.stdout.write("\n" + "💡 NEXT STEPS:")

        if Education.objects.count() == 0:
            self.stdout.write("   1. Run: python manage.py create_learning_sample_data")

        if SystemModule.objects.count() == 0:
            self.stdout.write("   2. Create some SystemModule objects (projects)")
            self.stdout.write("      Then run sample data command again for milestones")

        self.stdout.write("   3. Test HomeView to see dynamic learning journey")
        self.stdout.write("   4. Run: python manage.py generate_learning_analytics")
