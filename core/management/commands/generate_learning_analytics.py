# Command to generate learning analytics reports
# core/management/commands/generate_learning_analytics.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from datetime import date, timedelta
import json

from core.models import LearningJourneyManager, PortfolioAnalytics, Skill, Education
from projects.models import SystemModule, LearningMilestone, Technology
from blog.models import Post


class Command(BaseCommand):
    help = 'Generate learning analytics reports'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            choices=['json', 'markdown', 'console'],
            default='console',
            help='Output format for the report',
        )
        parser.add_argument(
            '--period',
            type=int,
            default=30,
            help='Period in days for analytics (default: 30)',
        )
        parser.add_argument(
            '--save-to-file',
            type=str,
            help='Save output to specified file path',
        )

    def handle(self, *args, **options):
        period = options['period']
        output_format = options['format']
        save_to_file = options['save_to_file']
        
        # Generate comprehensive analytics
        analytics_data = self.generate_analytics(period)
        
        # Generate output
        if output_format == 'json':
            output = self.format_json(analytics_data)
        elif output_format == 'markdown':
            output = self.format_markdown(analytics_data)
        else:
            output = self.format_console(analytics_data)
        
        # Save to file if specified
        if save_to_file:
            with open(save_to_file, 'w') as f:
                f.write(output)
            self.stdout.write(
                self.style.SUCCESS(f"Analytics saved to {save_to_file}")
            )
        else:
            self.stdout.write(output)

    def generate_analytics(self, period):
        """Generate comprehensive learning analytics"""
        journey_manager = LearningJourneyManager()
        
        try:
            learning_overview = journey_manager.get_journey_overview()
            skill_progression = journey_manager.get_skill_progression()
            learning_timeline = journey_manager.get_learning_timeline()
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"Could not generate some journey data: {e}")
            )
            learning_overview = self.get_fallback_overview()
            skill_progression = []
            learning_timeline = []
        
        return {
            'period_days': period,
            'generated_date': timezone.now().isoformat(),
            'learning_overview': learning_overview,
            'skill_progression': skill_progression[:10],  # Top 10 skills
            'learning_timeline': learning_timeline[:15],   # Recent 15 events
            'portfolio_analytics': self.get_portfolio_analytics(period),
            'system_stats': self.get_system_stats(),
            'content_stats': self.get_content_stats(period),
            'skill_stats': self.get_skill_stats(),
            'education_stats': self.get_education_stats(),
            'recommendations': self.get_recommendations(),
        }

    def get_fallback_overview(self):
        """Fallback overview if LearningJourneyManager fails"""
        return {
            'duration_years': '2+ Years',
            'courses_completed': Education.objects.filter(
                learning_type__in=['online_course', 'certification']
            ).count(),
            'projects_built': SystemModule.objects.filter(
                status__in=['deployed', 'published']
            ).count(),
            'skills_mastered': Skill.objects.filter(proficiency__gte=4).count(),
            'learning_hours': PortfolioAnalytics.objects.aggregate(
                total=Sum('learning_hours_logged')
            )['total'] or 0,
        }

    def get_portfolio_analytics(self, period):
        """Get portfolio analytics for specified period"""
        end_date = date.today()
        start_date = end_date - timedelta(days=period)
        
        analytics = PortfolioAnalytics.objects.filter(
            date__range=[start_date, end_date]
        ).aggregate(
            total_learning_hours=Sum('learning_hours_logged'),
            total_entries_written=Sum('datalog_entries_written'),
            total_skills_practiced=Sum('skills_practiced'),
            total_projects_worked=Sum('projects_worked_on'),
            total_milestones=Sum('milestones_achieved'),
            avg_daily_hours=Avg('learning_hours_logged'),
            active_days=Count('id', filter=Q(learning_hours_logged__gt=0)),
        )
        
        # Calculate additional metrics
        analytics['consistency_rate'] = (
            (analytics['active_days'] or 0) / period * 100
        ) if period > 0 else 0
        
        return analytics

    def get_system_stats(self):
        """Get system/project statistics"""
        return {
            'total_systems': SystemModule.objects.count(),
            'portfolio_ready': SystemModule.objects.filter(portfolio_ready=True).count(),
            'in_development': SystemModule.objects.filter(status='in_development').count(),
            'deployed': SystemModule.objects.filter(status='deployed').count(),
            'published': SystemModule.objects.filter(status='published').count(),
            'learning_stages': self.get_learning_stage_distribution(),
            'avg_completion': SystemModule.objects.aggregate(
                avg=Avg('completion_percent')
            )['avg'] or 0,
        }

    def get_learning_stage_distribution(self):
        """Get distribution of systems by learning stage"""
        stages = {}
        for choice in SystemModule.LEARNING_STAGE_CHOICES:
            stage_key, stage_label = choice
            count = SystemModule.objects.filter(learning_stage=stage_key).count()
            stages[stage_label] = count
        return stages

    def get_content_stats(self, period):
        """Get content statistics"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=period)
        
        return {
            'total_datalogs': Post.objects.filter(status='published').count(),
            'recent_datalogs': Post.objects.filter(
                status='published',
                published_date__gte=start_date
            ).count(),
            'total_milestones': LearningMilestone.objects.count(),
            'recent_milestones': LearningMilestone.objects.filter(
                date_achieved__gte=start_date
            ).count(),
            'featured_datalogs': Post.objects.filter(
                status='published',
                featured=True
            ).count(),
        }

    def get_skill_stats(self):
        """Get skill statistics"""
        skills_by_category = {}
        for category, label in Skill.CATEGORY_CHOICES:
            count = Skill.objects.filter(category=category).count()
            mastered = Skill.objects.filter(
                category=category,
                proficiency__gte=4
            ).count()
            skills_by_category[label] = {
                'total': count,
                'mastered': mastered,
                'percentage_mastered': (mastered / count * 100) if count > 0 else 0
            }
        
        return {
            'total_skills': Skill.objects.count(),
            'mastered_skills': Skill.objects.filter(proficiency__gte=4).count(),
            'learning_skills': Skill.objects.filter(is_currently_learning=True).count(),
            'featured_skills': Skill.objects.filter(is_featured=True).count(),
            'by_category': skills_by_category,
            'avg_proficiency': Skill.objects.aggregate(
                avg=Avg('proficiency')
            )['avg'] or 0,
        }

    def get_education_stats(self):
        """Get education statistics"""
        education_by_type = {}
        for choice in Education.LEARNING_TYPE_CHOICES:
            type_key, type_label = choice
            count = Education.objects.filter(learning_type=type_key).count()
            education_by_type[type_label] = count
        
        return {
            'total_education': Education.objects.count(),
            'completed_courses': Education.objects.filter(
                end_date__isnull=False
            ).count(),
            'current_courses': Education.objects.filter(is_current=True).count(),
            'with_certificates': Education.objects.filter(
                certificate_url__isnull=False
            ).exclude(certificate_url='').count(),
            'by_type': education_by_type,
            'total_hours': Education.objects.aggregate(
                total=Sum('hours_completed')
            )['total'] or 0,
        }

    def get_recommendations(self):
        """Get actionable recommendations"""
        recommendations = []
        
        # Systems without skills
        systems_without_skills = SystemModule.objects.annotate(
            skills_count=Count('skills_developed')
        ).filter(skills_count=0).count()
        
        if systems_without_skills > 0:
            recommendations.append({
                'category': 'Skills',
                'priority': 'High',
                'action': f'Add skill connections to {systems_without_skills} systems',
                'impact': 'Improves learning journey visibility'
            })
        
        # Portfolio readiness
        portfolio_candidates = SystemModule.objects.filter(
            completion_percent__gte=80,
            portfolio_ready=False
        ).count()
        
        if portfolio_candidates > 0:
            recommendations.append({
                'category': 'Portfolio',
                'priority': 'Medium',
                'action': f'Review {portfolio_candidates} systems for portfolio readiness',
                'impact': 'Increases employer-ready project count'
            })
        
        # Learning documentation
        recent_systems = SystemModule.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=60)
        ).annotate(
            milestones_count=Count('milestones')
        ).filter(milestones_count=0).count()
        
        if recent_systems > 0:
            recommendations.append({
                'category': 'Documentation',
                'priority': 'Medium',
                'action': f'Add learning milestones to {recent_systems} recent systems',
                'impact': 'Better learning progression tracking'
            })
        
        return recommendations

    def format_console(self, data):
        """Format analytics for console output"""
        output = []
        output.append("=" * 60)
        output.append("🚀 LEARNING JOURNEY ANALYTICS REPORT")
        output.append("=" * 60)
        output.append(f"Generated: {data['generated_date']}")
        output.append(f"Period: {data['period_days']} days")
        output.append("")
        
        # Overview
        overview = data['learning_overview']
        output.append("📊 LEARNING OVERVIEW")
        output.append("-" * 30)
        output.append(f"Learning Duration: {overview.get('duration_years', 'N/A')}")
        output.append(f"Total Learning Hours: {overview.get('learning_hours', 0)}")
        output.append(f"Courses Completed: {overview.get('courses_completed', 0)}")
        output.append(f"Projects Built: {overview.get('projects_built', 0)}")
        output.append(f"Skills Mastered: {overview.get('skills_mastered', 0)}")
        output.append("")
        
        # Recent Activity
        analytics = data['portfolio_analytics']
        output.append(f"📈 RECENT ACTIVITY ({data['period_days']} days)")
        output.append("-" * 30)
        output.append(f"Learning Hours: {analytics.get('total_learning_hours', 0):.1f}")
        output.append(f"DataLog Entries: {analytics.get('total_entries_written', 0)}")
        output.append(f"Skills Practiced: {analytics.get('total_skills_practiced', 0)}")
        output.append(f"Projects Worked: {analytics.get('total_projects_worked', 0)}")
        output.append(f"Learning Consistency: {analytics.get('consistency_rate', 0):.1f}%")
        output.append("")
        
        # System Stats
        system_stats = data['system_stats']
        output.append("🔧 SYSTEM STATISTICS")
        output.append("-" * 30)
        output.append(f"Total Systems: {system_stats['total_systems']}")
        output.append(f"Portfolio Ready: {system_stats['portfolio_ready']}")
        output.append(f"In Development: {system_stats['in_development']}")
        output.append(f"Average Completion: {system_stats['avg_completion']:.1f}%")
        output.append("")
        
        # Learning Stages
        output.append("Learning Stage Distribution:")
        for stage, count in system_stats['learning_stages'].items():
            output.append(f"  {stage}: {count}")
        output.append("")
        
        # Skill Stats
        skill_stats = data['skill_stats']
        output.append("🎯 SKILL STATISTICS")
        output.append("-" * 30)
        output.append(f"Total Skills: {skill_stats['total_skills']}")
        output.append(f"Mastered Skills: {skill_stats['mastered_skills']}")
        output.append(f"Currently Learning: {skill_stats['learning_skills']}")
        output.append(f"Average Proficiency: {skill_stats['avg_proficiency']:.1f}/5")
        output.append("")
        
        # Recommendations
        recommendations = data['recommendations']
        if recommendations:
            output.append("💡 RECOMMENDATIONS")
            output.append("-" * 30)
            for rec in recommendations:
                output.append(f"[{rec['priority']}] {rec['action']}")
                output.append(f"    Impact: {rec['impact']}")
            output.append("")
        
        output.append("=" * 60)
        return "\n".join(output)

    def format_json(self, data):
        """Format analytics as JSON"""
        return json.dumps(data, indent=2, default=str)

    def format_markdown(self, data):
        """Format analytics as Markdown"""
        output = []
        output.append("# 🚀 Learning Journey Analytics Report")
        output.append("")
        output.append(f"**Generated:** {data['generated_date']}")
        output.append(f"**Period:** {data['period_days']} days")
        output.append("")
        
        # Overview
        overview = data['learning_overview']
        output.append("## 📊 Learning Overview")
        output.append("")
        output.append(f"- **Learning Duration:** {overview.get('duration_years', 'N/A')}")
        output.append(f"- **Total Learning Hours:** {overview.get('learning_hours', 0)}")
        output.append(f"- **Courses Completed:** {overview.get('courses_completed', 0)}")
        output.append(f"- **Projects Built:** {overview.get('systems_built', 0)}")
        output.append(f"- **Skills Mastered:** {overview.get('skills_mastered', 0)}")
        output.append("")
        
        # Recent Activity
        analytics = data['portfolio_analytics']
        output.append(f"## 📈 Recent Activity ({data['period_days']} days)")
        output.append("")
        output.append(f"- **Learning Hours:** {analytics.get('total_learning_hours', 0):.1f}")
        output.append(f"- **DataLog Entries:** {analytics.get('total_entries_written', 0)}")
        output.append(f"- **Skills Practiced:** {analytics.get('total_skills_practiced', 0)}")
        output.append(f"- **Projects Worked:** {analytics.get('total_projects_worked', 0)}")
        output.append(f"- **Learning Consistency:** {analytics.get('consistency_rate', 0):.1f}%")
        output.append("")
        
        # Add more sections as needed...
        
        return "\n".join(output)