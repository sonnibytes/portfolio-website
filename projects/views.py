"""
Super simplified for new panel and model methods testing.
NOTE TO FUTURE ME: See archived_system_view.py in scratch or previous commits for all previous views.
"""

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views.decorators.http import require_http_methods
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy, reverse

from django.db.models import Count, Avg, Q, Sum, Max, Min, F, Prefetch, OuterRef, Case, When, Value, IntegerField
from django.db.models.functions import TruncMonth, Extract
from django.http import JsonResponse
from django.utils import timezone
from django.core.cache import cache

import re
from datetime import timedelta, datetime, date
import random
from collections import Counter, defaultdict

from .models import SystemModule, SystemType, Technology, SystemFeature, SystemMetric, SystemDependency, SystemImage, SystemSkillGain, LearningMilestone
from blog.models import Post, SystemLogEntry
from core.models import Skill, PortfolioAnalytics


# ===================== LEARNING FOCUSED VIEWS =====================

class LearningJourneyDashboardView(TemplateView):
    """
    Learning Journey Dashboard - showcases learning progression and skill development
    Uses the same beautiful AURA dashboard structure but with learning-focused data
    """
    template_name = "projects/learning_journey_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Core learning metrics for hero section
        context.update(
            {
                # Learning velocity metrics (replaces performance metrics)
                "learning_metrics": self.get_learning_metrics(),
                # Skills progression over time
                "skills_timeline": self.get_skills_timeline(),
                # Recent learning milestones (replaces system activity)
                "recent_milestones": self.get_recent_milestones(),
                # Technology mastery progression
                "technology_mastery": self.get_technology_mastery(),
                # Project complexity evolution
                "complexity_evolution": self.get_complexity_evolution(),
                # Portfolio readiness stats
                "portfolio_readiness": self.get_portfolio_readiness_stats(),
                # Learning stage distribution
                "learning_stages": self.get_learning_stage_distribution(),
                # Featured learning systems
                "featured_learning_systems": self.get_featured_learning_systems(),
            }
        )

        return context

    def get_learning_metrics(self):
        """Core learning metrics for dashboard hero section"""
        all_systems = SystemModule.objects.all()

        return {
            # Total learning volume
            'total_systems': all_systems.count(),
            'total_skills_gained': SystemSkillGain.objects.count(),
            'total_milestones': LearningMilestone.objects.count(),
            'portfolio_ready_count': all_systems.filter(portfolio_ready=True).count(),

            # Learning velocity (skills gained per month)
            'learning_velocity': self.calculate_learning_velocity(),

            # Technology diversity
            'technologies_mastered': self.get_technologies_with_multiple_systems(),

            # Time investment
            'total_learning_hours': self.get_total_learning_hours(),

            # Recent activity
            'days_since_last_system': self.get_days_since_last_system(),
        }

    def calculate_learning_velocity(self):
        """Calculate skills gained per month"""
        # Get first and latest skill gains
        first_gain = SystemSkillGain.objects.order_by('created_at').first()
        if not first_gain:
            return 0

        # Calculate months since first learning project
        months = max((timezone.now() - first_gain.created_at).days / 30, 1)
        total_skills = SystemSkillGain.objects.count()

        return round(total_skills / months, 2)

    def get_technologies_with_multiple_systems(self):
        """Count technologies used in 2+ projects/systems (shows progression)"""
        return Technology.objects.annotate(
            system_count=Count('systems')
        ).filter(system_count__gte=2).count()

    def get_total_learning_hours(self):
        """Sum of actual_dev_hours across all projects/systems"""
        total = SystemModule.objects.aggregate(
            total_hours=Sum('actual_dev_hours')
        )['total_hours'] or 0

        # Fallback to estimated hours if no actual hours
        if total == 0:
            total = SystemModule.objects.aggregate(
                total_hours=Sum('estimated_dev_hours')
            )['total_hours'] or 0

        return total

    def get_days_since_last_system(self):
        """Days since last project/system was updated"""
        latest = SystemModule.objects.order_by('-updated_at').first()
        if latest:
            return (timezone.now() - latest.updated_at).days
        return 0

    def get_skills_timeline(self):
        """Skills gained over time for timeline chart"""

        # Get skills gained by month for the last 12 months
        timeline = []
        current_date = timezone.now() - timedelta(days=365)

        while current_date <= timezone.now():
            month_start = current_date.replace(day=1)
            next_month = (month_start + timedelta(days=32)).replace(day=1)

            # Skills gained in projects/systems created this month
            month_skills = SystemSkillGain.objects.filter(
                system__created_at__gte=month_start,
                system__created_at__lt=next_month
            ).count()

            timeline.append({
                'month': month_start.strftime('%B %Y'),
                'month_short': month_start.strftime('%b'),
                'skills_gained': month_skills,
            })

            current_date = next_month

        return timeline

    def get_recent_milestones(self):
        """Recent learning milestones for activity feed"""
        return LearningMilestone.objects.select_related(
            'system', 'related_post', 'related_skill'
        ).order_by('-date_achieved')[:8]

    def get_technology_mastery(self):
        """Technology mastery progression"""
        tech_mastery = Technology.objects.annotate(
            system_count=Count('systems')
        ).filter(system_count__gt=0).order_by('-system_count')

        mastery_data = []
        for tech in tech_mastery:
            # Calculate mastery level based on project count
            if tech.system_count >= 5:
                mastery = 'expert'
            elif tech.system_count >= 3:
                mastery = 'advanced'
            elif tech.system_count >= 2:
                mastery = 'intermediate'
            else:
                mastery = 'beginner'

            mastery_data.append({
                'technology': tech,
                'system_count': tech.system_count,
                'mastery_level': mastery,
                'mastery_color': {
                    'beginner': '#FFB74D',
                    'intermediate': '#81C784',
                    'advanced': '#64B5F6',
                    'expert': '#FFD54F'
                }.get(mastery, '#81C784')
            })
        return mastery_data[:8]  # Top 8 Technologies

    def get_complexity_evolution(self):
        """System/Project complexity evolution over time"""
        systems = SystemModule.objects.order_by("created_at")

        evolution = []
        for system in systems:
            evolution.append(
                {
                    "system": system.title,
                    "date": system.created_at,
                    "complexity_score": system.get_complexity_evolution_score(),
                    "learning_stage": system.learning_stage,
                    "learning_stage_color": system.get_learning_stage_color(),
                }
            )

        return evolution

    def get_portfolio_readiness_stats(self):
        """Portfolio readiness statistics"""
        all_systems = SystemModule.objects.all()

        if not all_systems.exists():
            return {
                "ready_count": 0,
                "total_count": 0,
                "ready_percentage": 0,
                "needs_work": [],
            }

        ready_count = all_systems.filter(portfolio_ready=True).count()
        total_count = all_systems.count()

        return {
            "ready_count": ready_count,
            "total_count": total_count,
            "ready_percentage": round((ready_count / total_count) * 100, 1),
            "needs_work": all_systems.filter(
                portfolio_ready=False, status__in=["deployed", "published"]
            )[:3],  # Top 3 that need portfolio prep
        }

    def get_learning_stage_distribution(self):
        """Distribution of projects/systems by learning stage"""
        stages = (
            SystemModule.objects.values("learning_stage")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        stage_data = []
        for stage in stages:
            stage_data.append(
                {
                    "stage": stage["learning_stage"],
                    "stage_display": dict(SystemModule.LEARNING_STAGE_CHOICES).get(
                        stage["learning_stage"], stage["learning_stage"]
                    ),
                    "count": stage["count"],
                    "color": {
                        "tutorial": "#FFB74D",
                        "guided": "#81C784",
                        "independent": "#64B5F6",
                        "refactoring": "#BA68C8",
                        "contributing": "#4FC3F7",
                        "teaching": "#FFD54F",
                    }.get(stage["learning_stage"], "#64B5F6"),
                }
            )

        return stage_data

    def get_featured_learning_systems(self):
        """Featured systems with learning focus"""
        return (
            SystemModule.objects.featured()
            .select_related("system_type")
            .prefetch_related("technologies", "skills_developed")
            .order_by("-updated_at")[:6]
        )


class EnhancedLearningSystemListView(ListView):
    """
    Learning-Focused System List - Transform existing system list to showcase
    learning progression instead of performance metrics.

    Features:
    - Learning stage filtering (tutorial → independent → teaching)
    - Skills gained filtering and display
    - Portfolio readiness indicators
    - Time investment tracking
    - Learning velocity calculations
    """

    model = SystemModule
    # template_name = "projects/system_list.html"  # Reuse existing template with learning context
    template_name = "projects/learning_system_list.html"  # Replace main system_list once cleaned up
    context_object_name = "systems"
    paginate_by = 12

    def get_queryset(self):
        """Enhanced query with learning-focused optimizations"""
        # Start with optimized base query for learning data
        queryset = (
            SystemModule.objects.select_related("system_type", "author")
            .prefetch_related(
                "technologies",
                "skills_developed",  # Important for learning cards
                "milestones",  # For recent achievements
                "skill_gains__skill",  # For skill gain details
            )
            .order_by("-updated_at")
        )

        # LEARNING STAGE FILTERING (replaces status filtering)
        learning_stage = self.request.GET.get("learning_stage")
        if learning_stage:
            queryset = queryset.filter(learning_stage=learning_stage)

        # PORTFOLIO READINESS FILTERING
        portfolio_ready = self.request.GET.get("portfolio_ready")
        if portfolio_ready == "ready":
            queryset = queryset.filter(portfolio_ready=True)
        elif portfolio_ready == "in_progress":
            queryset = queryset.filter(portfolio_ready=False)

        # SKILLS FILTERING
        skill_filter = self.request.GET.get("skill")
        if skill_filter:
            queryset = queryset.filter(skills_developed__slug=skill_filter)

        # TIME INVESTMENT FILTERING
        time_filter = self.request.GET.get("time_investment")
        if time_filter == "short":  # <20 hours
            queryset = queryset.filter(actual_dev_hours__lt=20)
        elif time_filter == "medium":  # 20-50 hours
            queryset = queryset.filter(actual_dev_hours__range=[20, 50])
        elif time_filter == "long":  # 50+ hours
            queryset = queryset.filter(actual_dev_hours__gte=50)

        # Technology filter (keep existing)
        tech_filter = self.request.GET.get("tech")
        if tech_filter:
            queryset = queryset.filter(technologies__slug=tech_filter)

        # Search across learning-relevant fields
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(skills_developed__name__icontains=search)
                | Q(technologies__name__icontains=search)
            ).distinct()

        # LEARNING-FOCUSED ORDERING
        order = self.request.GET.get("order", "recent")
        if order == "recent":
            queryset = queryset.order_by("-updated_at")
        elif order == "learning_velocity":
            # Order by skills gained per month (calculated on-the-fly)
            queryset = queryset.annotate(
                skills_count=Count("skills_developed")
            ).order_by("-skills_count")
        elif order == "complexity_evolution":
            # Order by complexity progression
            queryset = queryset.order_by("-complexity", "-updated_at")
        elif order == "portfolio_readiness":
            # Portfolio ready items first
            queryset = queryset.order_by("-portfolio_ready", "-updated_at")
        elif order == "time_investment":
            # Use actual_dev_hours w fallback to estimated_dev_hours
            queryset = queryset.order_by(
                F('actual_dev_hours').desc(nulls_last=True),
                F('estimated_dev_hours').desc(nulls_last=True),
                "-updated_at"
            )
        elif order == "learning_stage":
            # Custom ordering by learning stage progression
            stage_order = Case(
                When(learning_stage='tutorial', then=Value(1)),
                When(learning_stage='guided', then=Value(2)),
                When(learning_stage='independent', then=Value(3)),
                When(learning_stage='refactoring', then=Value(4)),
                When(learning_stage='contributing', then=Value(5)),
                When(learning_stage='teaching', then=Value(6)),
                default=Value(0),
                output_field=IntegerField(),
            )
            queryset = queryset.order_by(stage_order=stage_order).order_by('-stage_order', '-updated_at')

        return queryset

    def get_context_data(self, **kwargs):
        """Enhanced context with learning-focused metrics and filters"""
        context = super().get_context_data(**kwargs)

        # LEARNING METRICS FOR SIDEBAR (replaces performance metrics)
        context.update(
            {
                # Learning stage distribution
                "learning_stage_stats": self.get_learning_stage_distribution(),

                # Portfolio readiness stats
                "portfolio_stats": self.get_portfolio_readiness_stats(),

                # Skills statistics
                "skills_stats": self.get_skills_statistics(),

                # Time investment breakdown
                "time_investment_stats": self.get_time_investment_stats(),

                # Technology mastery (enhanced with learning context)
                "tech_mastery": self.get_technology_mastery(),

                # Available filter options
                "available_skills": self.get_available_skills(),
                "available_learning_stages": SystemModule.LEARNING_STAGE_CHOICES,

                # Current filters for display
                "active_filters": self.get_active_learning_filters(),

                # Recent learning activity
                "recent_milestones": LearningMilestone.objects.select_related(
                    'system', 'related_skill'
                ).order_by("-date_achieved")[:5],

                # Quick stats for header (learning-focused)
                'quick_stats': self.get_learning_quick_stats(),
            }
        )

        return context

    def get_learning_stage_distribution(self):
        """Get count of systems by learning stage"""
        distribution = {}
        for stage_code, stage_name in SystemModule.LEARNING_STAGE_CHOICES:
            count = SystemModule.objects.filter(learning_stage=stage_code).count()
            distribution[stage_code] = {
                "name": stage_name,
                "count": count,
                "color": self.get_learning_stage_color(stage_code),
            }
        return distribution

    def get_portfolio_readiness_stats(self):
        """Get portfolio readiness breakdown"""
        total_systems = SystemModule.objects.count()
        ready_count = SystemModule.objects.filter(portfolio_ready=True).count()

        return {
            "ready": ready_count,
            "in_progress": total_systems - ready_count,
            "total": total_systems,
            "ready_percentage": round(
                (ready_count / total_systems * 100) if total_systems > 0 else 0, 1
            ),
        }

    def get_skills_statistics(self):
        """Get skills development statistics"""
        # Skills with most systems
        top_skills = (
            Skill.objects.annotate(systems_count=Count("project_gains"))
            .filter(systems_count__gt=0)
            .order_by("-systems_count")[:8]
        )

        total_skill_gains = SystemSkillGain.objects.count()
        total_systems = SystemModule.objects.count()

        return {
            "total_skills": SystemSkillGain.objects.values("skill").distinct().count(),
            "total_skill_gains": total_skill_gains,
            "top_skills": top_skills,
            "avg_skills_per_system": round(total_skill_gains / max(total_systems, 1), 1)
        }

    def get_time_investment_stats(self):
        """Get time investment distribution"""
        # Use actual_dev_hours primarily, w estimated as fallback
        systems_with_actual_time = SystemModule.objects.exclude(actual_dev_hours__isnull=True)
        systems_with_estimated_time = SystemModule.objects.exclude(estimated_dev_hours__isnull=True)

        # Combine acctual and estimated for broader coverage
        actual_total = systems_with_actual_time.aggregate(total=Sum('actual_dev_hours'))['total'] or 0
        estimated_total = systems_with_estimated_time.aggregate(total=Sum('estimated_dev_hours'))['total'] or 0

        # For categorization, prioritize actual hours but use estimated as fallback
        short_count = systems_with_actual_time.filter(actual_dev_hours__lt=20).count()
        medium_count = systems_with_actual_time.filter(actual_dev_hours__range=[20, 50]).count()
        long_count = systems_with_actual_time.filter(actual_dev_hours__gte=50).count()

        # If no actual hours, use estimated
        if short_count + medium_count + long_count == 0:
            short_count = systems_with_estimated_time.filter(estimated_dev_hours__lt=20).count()
            medium_count = systems_with_estimated_time.filter(estimated_dev_hours__range=[20, 50]).count()
            long_count = systems_with_estimated_time.filter(estimated_dev_hours__gte=50).count()

        return {
            'short': short_count,
            'medium': medium_count,
            'long': long_count,
            'total_hours': actual_total or estimated_total,
            'avg_hours': round((actual_total or estimated_total) / max(SystemModule.objects.count(), 1), 1),
            'systems_with_time_data': systems_with_actual_time.count() or systems_with_estimated_time.count(),
        }

    def get_technology_mastery(self):
        """Get technology usage with learning context"""

        # Technologies with system count and learning stage progression
        tech_stats = defaultdict(lambda: {"systems": 0, "stages": set()})

        for system in SystemModule.objects.prefetch_related("technologies"):
            for tech in system.technologies.all():
                tech_stats[tech]["systems"] += 1
                tech_stats[tech]["stages"].add(system.learning_stage)

        # Convert to list with mastery indicators
        mastery_list = []
        for tech, stats in tech_stats.items():
            mastery_level = "beginner"
            if stats["systems"] >= 3:
                mastery_level = "intermediate"
            if "teaching" in stats["stages"] or stats["systems"] >= 5:
                mastery_level = "advanced"

            mastery_list.append(
                {
                    "technology": tech,
                    "systems_count": stats["systems"],
                    "mastery_level": mastery_level,
                    "progression": len(stats["stages"]),  # Stages used across
                }
            )

        return sorted(mastery_list, key=lambda x: x["systems_count"], reverse=True)[:8]

    def get_available_skills(self):
        """Get skills available for filtering"""

        return (
            Skill.objects.filter(project_gains__isnull=False)
            .distinct()
            .order_by("name")
        )

    def get_active_learning_filters(self):
        """Get currently active learning-focused filters"""
        filters = {}

        if self.request.GET.get("learning_stage"):
            stage_code = self.request.GET.get("learning_stage")
            stage_name = dict(SystemModule.LEARNING_STAGE_CHOICES).get(
                stage_code, stage_code
            )
            filters["Learning Stage"] = stage_name

        if self.request.GET.get("portfolio_ready"):
            ready_map = {"ready": "Portfolio Ready", "in_progress": "In Progress"}
            filters["Portfolio Status"] = ready_map.get(
                self.request.GET.get("portfolio_ready")
            )

        if self.request.GET.get("skill"):
            try:
                skill = Skill.objects.get(slug=self.request.GET.get("skill"))
                filters["Skill"] = skill.name
            except:
                pass

        if self.request.GET.get("time_investment"):
            time_map = {
                "short": "Short (<20h)",
                "medium": "Medium (20-50h)",
                "long": "Long (50h+)",
            }
            filters["Time Investment"] = time_map.get(
                self.request.GET.get("time_investment")
            )

        if self.request.GET.get("tech"):
            try:
                tech = Technology.objects.get(slug=self.request.GET.get("tech"))
                filters["Technology"] = tech.name
            except:
                pass

        if self.request.GET.get("search"):
            filters["Search"] = self.request.GET.get("search")

        return filters

    def get_learning_quick_stats(self):
        """Quick stats for header using learning metrics"""
        total_systems = SystemModule.objects.count()

        return {
            'total_systems': total_systems,
            'portfolio_ready_count': SystemModule.objects.filter(portfolio_ready=True).count(),
            'skills_gained_count': SystemSkillGain.objects.count(),
            'learning_stages_count': SystemModule.objects.values('learning_stage').distinct().count(),
            'recent_milestones_count': LearningMilestone.objects.filter(
                date_achieved__gte=timezone.now() - timezone.timedelta(days=30)
            ).count()
        }

    def get_learning_stage_color(self, stage_code):
        """Get color for learning stage badges"""
        colors = {
            "tutorial": "orange",  # Learning/following
            "guided": "yellow",  # Guided practice
            "independent": "teal",  # Independent work
            "refactoring": "purple",  # Improving/optimizing
            "contributing": "mint",  # Contributing to others
            "teaching": "gold",  # Sharing knowledge
        }
        return colors.get(stage_code, "gray")


class LearningSystemControlInterfaceView(DetailView):
    """
    Learning-Focused System Control Interface

    Transform existing SystemControlInterfaceView to showcase learning progression
    instead of performance metrics while maintaining the beautiful 8-panel structure.

    Key Changes:
    - Overview Panel: Learning metrics instead of performance metrics
    - Skills Panel: Detailed skill progression (replaces Details panel)
    - Learning Timeline: Milestones and breakthroughs (replaces Performance panel)
    - Portfolio Assessment: Readiness breakdown (new panel)
    - Keep: DataLogs, Technologies, Features, Dependencies panels (already learning-relevant)
    """

    model = SystemModule
    template_name = "projects/learning_system_control_interface.html"
    context_object_name = "system"

    def get_queryset(self):
        # Optimized for learning data
        return SystemModule.objects.select_related(
            'system_type', 'author'
        ).prefetch_related(
            'technologies',
            'skills_developed',
            'skill_gains__skill',   # For detailed skill progression
            'milestones',           # For learning timeline
            'features',
            'dependencies',
            'log_entries__post',    # DataLogs integration
            'log_entries__post__category',
            'log_entries__post__tags'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        system = self.object

        # Define comprehensive control panels (system info + learning focused)
        context["control_panels"] = [
            {
                "id": "overview",
                "name": "System Overview",
                "icon": "tachometer-alt",
                "description": "System metrics, technologies, and recent activity",
                "count": None,
            },
            {
                "id": "details",
                "name": "System Details",
                "icon": "file-alt",
                "description": "Technical documentation and system specifications",
                "count": None,
            },
            {
                "id": "learning_overview",
                "name": "Learning Overview",
                "icon": "chart-line",
                "description": "Learning metrics and project development progression",
                "count": None,
            },
            {
                "id": "skills",
                "name": "Skills Developed",
                "icon": "brain",
                "description": "Detailed skill progression and competency gains",
                "count": system.skills_developed.count(),
            },
            {
                "id": "timeline",
                "name": "Learning Timeline",
                "icon": "timeline",
                "description": "Milestones, breakthroughs, and development history",
                "count": system.milestones.count(),
            },
            {
                "id": "portfolio",
                "name": "Portfolio Assessment",
                "icon": "clipboard-check",
                "description": "Portfolio readiness analysis and recommendations",
                "count": None,
            },
            {
                "id": "datalogs",
                "name": "DataLogs",
                "icon": "file-text",
                "description": "Learning documentation and related posts",
                "count": system.get_related_logs().count(),
            },
            {
                "id": "technologies",
                "name": "Technologies",
                "icon": "cogs",
                "description": "Technology stack analysis and learning context",
                "count": system.technologies.count(),
            },
            {
                "id": "features",
                "name": "Features",
                "icon": "list",
                "description": "Feature development and implementation challenges",
                "count": system.features.count(),
            },
            {
                "id": "dependencies",
                "name": "Dependencies",
                "icon": "link",
                "description": "External dependencies and integration challenges",
                "count": system.dependencies.count(),
            },
        ]

        # Active panel (default to overview)
        context['active_panel'] = self.request.GET.get('panel', 'overview')

        # Panel-specific data
        context['panel_data'] = self.get_panel_data(system, context['active_panel'])

        return context

    def get_panel_data(self, system, active_panel):
        """Generate data for each learning-focused panel"""

        if active_panel == "overview":
            return self.get_system_overview_data(system)
        elif active_panel == "details":
            return self.get_system_details_data(system)
        elif active_panel == "learning_overview":
            return self.get_learning_overview_data(system)
        elif active_panel == "skills":
            return self.get_skills_progression_data(system)
        elif active_panel == "timeline":
            return self.get_learning_timeline_data(system)
        elif active_panel == "portfolio":
            return self.get_portfolio_assessment_data(system)
        elif active_panel == "datalogs":
            return self.get_datalogs_data(system)
        elif active_panel == "technologies":
            return self.get_tech_learning_data(system)
        elif active_panel == "features":
            return self.get_features_learning_data(system)
        elif active_panel == "dependencies":
            return self.get_dependencies_data(system)

        return {}

    def get_system_overview_data(self, system):
        """System overview panel - basic system info, tech, recent activity"""
        return {
            'system_metrics': {
                'status': system.status,
                'status_display': system.get_status_display(),
                'completion_percent': float(system.completion_percent),
                'complexity': system.complexity,
                'priority': system.priority,
                'created_date': system.created_at,
                'last_updated': system.updated_at,
            },
            'technology_summary': {
                'technologies': system.technologies.all()[:8],
                'total_count': system.technologies.count(),
                'primary_languages': system.technologies.filter(
                    category__in=['Programming Language', 'Framework']
                )[:4],
            },
            'development_stats': {
                'lines_of_code': system.code_lines,
                'commit_count': system.commit_count,
                'last_commit': system.last_commit_date,
                'estimated_hours': system.estimated_dev_hours,
                'actual_hours': system.actual_dev_hours,
            },
            'system_health': {
                'status': system.get_health_status() if hasattr(system, 'get_health_status') else 'unknown',
                'deployment_ready': system.status == 'deployed',
                'has_documentation': bool(system.description),
                'has_features': system.features.count() > 0,
            },
            'recent_activity': self.get_recent_activity_feed(system),
            'quick_links': {
                'github_url': system.github_url,
                'live_url': system.live_url or system.demo_url,
                'documentation_url': system.documentation_url,
            }
        }

    def get_system_details_data(self, system):
        """System details panel data (markdown content and technical specs)"""
        return {
            'descriptions': {
                'main_description': system.description,
                'brief_description': system.excerpt,
                'technical_details': getattr(system, 'technical_details', None),
                # Leaving bc might add setup and usage
                'setup_instructions': getattr(system, 'setup_instructions', None),
                'usage_examples': getattr(system, 'usage_examples', None),
                # Probably won't add, but just in case
                'deployment_notes': getattr(system, 'deployment_notes', None),
            },
            'specifications': {
                'system_type': system.system_type,
                'complexity_level': system.complexity,
                'estimated_timeline': f"{system.estimated_dev_hours} hours" if system.estimated_dev_hours else None,
            },
            'architecture_info': {
                'architecture_diagram': system.architecture_diagram,
                # May add? Not sure
                'database_schema': getattr(system, 'database_schema', None),
                'api_documentation': getattr(system, 'api_documentation', None),
                'security_considerations': getattr(system, 'security_considerations', None),
            },
            'learning_context': {
                'skills_developed': getattr(system, 'skills_developed', None),
                'challenges': getattr(system, 'challenges', None),
            }
        }

    def get_recent_activity_feed(self, system):
        """Generate recent activity feed for system overview"""
        activity = []

        # Recent commits
        if system.last_commit_date:
            activity.append({
                'type': 'commit',
                'date': system.last_commit_date,
                'description': f"Latest commit pushed ({system.commit_count} total)",
                'icon': 'code-branch',
                'color': 'teal'
            })

        # Recent milestones
        recent_milestones = system.milestones.order_by("-date_achieved")[:3]
        for milestone in recent_milestones:
            activity.append(
                {
                    "type": "milestone",
                    "date": milestone.date_achieved,
                    "description": milestone.title,
                    "icon": self.get_milestone_icon(milestone.milestone_type),
                    "color": self.get_milestone_color(milestone.milestone_type),
                }
            )

        # System Updates
        if system.updated_at != system.created_at:
            activity.append({
                'type': 'update',
                'date': system.updated_at,
                'description': 'System information updated',
                'icon': 'edit',
                'color': 'info'
            })

        # Recent DataLogs
        recent_logs = system.get_related_logs()[:3]
        for log in recent_logs:
            activity.append({
                'type': 'datalog',
                'date': log.post.created_at,
                'description': f"DataLog: {log.post.title}",
                'icon': 'file-text',
                'color': 'lavender',
            })

        # Sort by date and return recent items
        activity.sort(key=lambda x: x['date'], reverse=True)
        return activity[:8]

    def get_related_challenge_logs(self, system):
        """Find DataLogs related to system challenges"""
        if not system.challenges:
            return []

        challenges_logs = []
        if system.challenges:
            # Search for DataLogs that might address challenges mentioned in challenges field
            challenges_keywords = self.extract_keywords_from_markdown(system.challenges)

            # Find posts that contain challenge-related keywords
            for keyword in challenges_keywords[:5]:  # Limit to top 5 keywords
                related_posts = system.log_entries.select_related("post").filter(
                    Q(post__title__icontains=keyword)
                    | Q(post__content__icontains=keyword)
                    | Q(post__excerpt__icontains=keyword)
                )[:3]
                for entry in related_posts:
                    if entry not in challenges_logs:
                        challenges_logs.append(
                            {
                                "log_entry": entry,
                                "keyword": keyword,
                                "relevance": "addresses challenges",
                            }
                        )
        return challenges_logs[:3]

    def extract_keywords_from_markdown(self, markdown_content):
        """Extract key terms from markdown content for finding related logs."""
        if not markdown_content:
            return []

        # Remove additional formatting
        text = re.sub(r"[#*`\[\]()_-]", " ", markdown_content)

        # Split into words and filter for meaningful terms
        words = text.lower().split()

        # Filter out common words and keep technical terms
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'was', 'are', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}

        keywords = [word for word in words if len(word) > 3 and word not in stopwords]

        # Count frequency and return top keywords
        word_counts = Counter(keywords)

        return [word for word, count in word_counts.most_common(10)]

    def get_learning_overview_data(self, system):
        """Learning metrics for overview panel (replaces performance metrics)"""
        stats = system.get_development_stats_for_learning()

        return {
            "learning_stage": {
                "current": system.learning_stage,
                "display": system.get_learning_stage_display(),
                "color": system.get_learning_stage_color(),
                "next_stage": self.get_next_learning_stage(system.learning_stage),
            },
            "skills_summary": {
                "total_count": system.skills_developed.count(),
                "primary_skills": list(system.skills_developed.all()[:4]),
                "skills_text": system.get_skills_summary(),
            },
            "development_progress": {
                "completion_score": float(system.completion_percent),
                "portfolio_ready": system.portfolio_ready,
                "readiness_score": system.get_portfolio_readiness_score(),
                "complexity_evolution": system.get_complexity_evolution_score(),
            },
            "time_investment": {
                "estimated_hours": stats["estimated_hours"],
                "actual_hours": stats["actual_hours"],
                "efficiency": self.calculate_learning_efficiency(stats),
                "investment_level": system.get_time_investment_level(),
            },
            "code_metrics": {
                "lines_of_code": stats["lines_of_code"],
                "commits": stats["commits"],
                "last_commit": stats["last_commit"],
                "activity_level": self.get_activity_level(stats),
            },
            "learning_velocity": {
                "skills_per_month": system.get_learning_velocity(),
                "complexity_growth": stats["complexity_score"],
                "milestone_count": system.milestones.count(),
            },
        }

    def get_skills_progression_data(self, system):
        """Detailed skills analysis (replaces Details panel)"""
        skill_gains = system.skill_gains.select_related('skill').all()

        skills_analysis = []
        for gain in skill_gains:
            skills_analysis.append({
                'skill': gain.skill,
                'proficiency_gained': gain.proficiency_gained,
                'how_learned': gain.how_learned,
                'has_breakthrough_moment': gain.skill.has_breakthroughs(),
                'breakthrough_moments': gain.skill.get_breakthrough_moments(),
                'mastery_level': gain.skill.get_mastery_level(),
                'other_systems': gain.skill.get_systems_using_skill().exclude(system=system)[:3],
                'progression': gain.skill.get_learning_progression()
            })

        return {
            'skills_analysis': skills_analysis,
            'skill_categories': self.categorize_skills(skill_gains),
            'learning_focus': self.identify_learning_focus(skill_gains),
            'skill_gaps': self.identify_skill_gaps(system),
            'recommended_next_skills': self.get_recommended_skills(system)
        }

    def get_learning_timeline_data(self, system):
        """Learning milestones adn timeline (replaces performance panel)"""
        milestones = system.milestones.order_by('date_achieved')

        timeline_events = []

        # Add project start
        if system.start_date:
            timeline_events.append({
                'date': system.start_date,
                'type': 'project_start',
                'title': 'Project Started',
                'description': f'Began development in {system.learning_stage} stage',
                'icon': 'play',
                'color': 'teal'
            })

        # Add milestones
        for milestone in milestones:
            timeline_events.append({
                'date': milestone.date_achieved.date(),
                'type': 'milestone',
                'title': milestone.title,
                'description': milestone.description,
                'milestone_type': milestone.milestone_type,
                'icon': self.get_milestone_icon(milestone.milestone_type),
                'color': self.get_milestone_color(milestone.milestone_type),
                'related_post': milestone.related_post
            })

        # Add skill gains
        for gain in system.skill_gains.all():
            if gain.skill.has_breakthroughs():
                breakthroughs = gain.skill.get_breakthrough_moments()
                for moment in breakthroughs:
                    timeline_events.append({
                        'date': moment['date'].date(),  # Appx - could be more specific
                        'type': 'skill_breakthrough',
                        'title': f'{gain.skill.name} Breakthrough',
                        'description': moment['learning_story'],
                        'icon': 'lightbulb',
                        'color': 'yellow'
                    })

        # Sort by date
        timeline_events.sort(key=lambda x: x['date'])

        return {
            'timeline_events': timeline_events,
            'learning_duration': self.calculate_learning_duration(system),
            'major_breakthroughs': milestones.filter(milestone_type__in=['breakthrough', 'first_time']).count(),
            'completion_milestones': milestones.filter(
                milestone_type='completion'
            ).count()
        }

    def get_portfolio_assessment_data(self, system):
        """Portfolio readiness assessment (new panel)"""
        assessment = {
            'overall_ready': system.portfolio_ready,
            'readiness_score': system.get_portfolio_readiness_score(),
            'assessment_criteria': []
        }

        # Assess different criteria
        criteria = [
            {
                "name": "Code Quality",
                "weight": 25,
                "score": self.assess_code_quality(system),
                "description": "Clean, well-structured, documented code",
            },
            {
                "name": "Feature Completeness",
                "weight": 20,
                "score": self.assess_feature_completeness(system),
                "description": "Core features implemented and working",
            },
            {
                "name": "Documentation",
                "weight": 20,
                "score": self.assess_documentation(system),
                "description": "Clear README, setup instructions, usage examples",
            },
            {
                "name": "Technology Showcase",
                "weight": 15,
                "score": self.assess_tech_showcase(system),
                "description": "Demonstrates relevant technical skills",
            },
            {
                "name": "Learning Evidence",
                "weight": 10,
                "score": self.assess_learning_evidence(system),
                "description": "Shows learning progression and growth",
            },
            {
                "name": "Deployment/Demo",
                "weight": 10,
                "score": self.assess_deployment(system),
                "description": "Live demo or deployment available",
            },
        ]

        assessment['assessment_criteria'] = criteria
        assessment['weighted_score'] = sum(
            c['score'] * c['weight'] / 100 for c in criteria
        )

        # Recommendations
        assessment['recommendations'] = self.get_portfolio_recommendations(system, criteria)

        return assessment

    def get_datalogs_data(self, system):
        """DataLogs integration (keep existing structure)"""
        related_logs = system.get_related_logs()

        return {
            'related_logs': related_logs[:10],
            'learning_posts': related_logs.filter(post__excerpt__icontains='learn')[:5],
            'challenge_posts': related_logs.filter(post__excerpt__icontains='challenge')[:5],
            'has_documentation': related_logs.exists(),
            'documentation_completeness': self.assess_documentation_completeness(system, related_logs)
        }

    def get_tech_learning_data(self, system):
        """Technology analysis with learning context"""
        tech_analysis = []

        for tech in system.technologies.all():
            analysis = {
                'technology': tech,
                'learning_context': self.get_tech_learning_context(tech, system),
                'skill_connections': system.skills_developed.filter(name__icontains=tech.name),
                'other_uses': tech.systems.exclude(id=system.id)[:3],
                'mastery_level': self.assess_tech_mastery(tech, system),
                'learning_impact': self.assess_tech_learning_impact(tech, system)
            }
            tech_analysis.append(analysis)

        return {
            'tech_analysis': tech_analysis,
            'primary_stack': tech_analysis[:4],
            'learning_new_techs': [t for t in tech_analysis if t['learning_context'] == 'first_time'],
            'mastery_showcase': [t for t in tech_analysis if t['mastery_level'] >= 'intermediate']
        }

    def get_features_learning_data(self, system):
        """Features with learning challenges context"""
        features_data = []

        for feature in system.features.all():
            feature_data = {
                'feature': feature,
                'learning_challenges': self.extract_learning_challenges(feature),
                'skills_applied': self.map_feature_to_skills(feature, system),
                'complexity_contribution': self.assess_feature_complexity(feature),
                'implementation_insights': self.get_implementation_insights(feature)
            }
            features_data.append(feature_data)

        return {
            'features_data': features_data,
            'challenging_features': [f for f in features_data if f['complexity_contribution'] >= 7],
            'skill_development_features': [f for f in features_data if f['skills_applied']],
            'learning_moments': self.identify_feature_learning_moments(features_data)
        }

    def get_dependencies_data(self, system):
        """Dependencies with learning integration context"""
        deps_data = []

        for dep in system.dependencies.all():
            dep_data = {
                'dependency': dep,
                'learning_rationale': self.get_dependency_learning_context(dep),
                'integration_challenges': self.assess_integration_complexity(dep),
                'skill_requirements': self.map_dependency_skills(dep, system),
                'alternative_options': self.suggest_alternatives(dep)
            }
            deps_data.append(dep_data)

        return {
            'dependencies_data': deps_data,
            'learning_dependencies': [d for d in deps_data if d['learning_rationale']],
            'complex_integrations': [d for d in deps_data if d['integration_challenges'] >= 7],
            'skill_expanding': [d for d in deps_data if d['skill_requirements']]
        }

    # Helper methods for learning assessment
    def get_next_learning_stage(self, current_stage):
        """Suggest next learning stage"""
        progression = {
            'tutorial': 'guided',
            'guided': 'independent',
            'independent': 'refactoring',
            'refactoring': 'contributing',
            'contributing': 'teaching',
            'teaching': 'mentoring'
        }
        return progression.get(current_stage, 'advanced')

    def calculate_learning_efficiency(self, stats):
        """Calculate learning efficiency ratio"""
        if stats['estimated_hours'] and stats['actual_hours']:
            return stats['estimated_hours'] / stats['actual_hours']
        return 1.0

    def get_activity_level(self, stats):
        """Determine development activity level"""
        commits = stats['commits']
        if commits >= 100:
            return 'high'
        elif commits >= 50:
            return 'medium'
        elif commits >= 20:
            return 'low'
        else:
            return 'minimal'

    def categorize_skills(self, skill_gains):
        """Categorize skills by type"""
        categories = {'technical': [], 'soft': [], 'tools': []}

        for gain in skill_gains:
            category = gain.skill.category.lower() if gain.skill.category else 'technical'
            if category in categories:
                categories[category].append(gain)
            else:
                categories['technical'].append(gain)

        return categories

    def identify_learning_focus(self, skill_gains):
        """Identify main learning focus areas"""
        focus_areas = {}
        for gain in skill_gains:
            area = gain.skill.category or 'General'
            focus_areas[area] = focus_areas.get(area, 0) + 1

        return sorted(focus_areas.items(), key=lambda x: x[1], reverse=True)[:3]

    def identify_skill_gaps(self, system):
        """Identify potential skill gaps"""
        # This could be enhanced w more sophisticated analysis
        # TODO: Logic Enhancement
        common_skills = ['testing', 'documentation', 'deployment', 'security']
        current_skills = set(system.skills_developed.values_list('name', flat=True))

        gaps = [skill for skill in common_skills if not any(skill.lower() in cs.lower() for cs in current_skills)]

        return gaps[:3]

    def get_recommended_skills(self, system):
        """Recommend next skills to learn"""
        # Based on technologies used and current skill level
        recommendations = []

        # Simple rec logic (can be enhanced)
        # TODO: Logic Enhancement
        for tech in system.technologies.all():
            if 'python' in tech.name.lower():
                recommendations.extend(['testing', 'async programming', 'packaging'])
            elif 'django' in tech.name.lower():
                recommendations.extend(['django rest framework', 'celery', 'caching'])
            elif 'javascript' in tech.name.lower():
                recommendations.extend(['typescript', 'testing', 'bundling'])

        # Remove dupes and skills already learned
        current_skills = set(system.skills_developed.values_list('name', flat=True))

        recommendations = list(set(recommendations) - current_skills)

        return recommendations[:4]

    def get_milestone_icon(self, milestone_type):
        """Get appropriate icon for milestone type"""
        icons = {
            "first_time": "star",
            "breakthrough": "lightbulb",
            "completion": "check-circle",
            "deployment": "rocket",
            "teaching": "users",
            "contribution": "code-branch",
        }
        return icons.get(milestone_type, "flag")

    def get_milestone_color(self, milestone_type):
        """Get appropriate color for milestone type"""
        colors = {
            "first_time": "yellow",
            "breakthrough": "purple",
            "completion": "teal",
            "deployment": "coral",
            "teaching": "mint",
            "contribution": "lavender",
        }
        return colors.get(milestone_type, "navy")

    def calculate_learning_duration(self, system):
        """Calculate total learning/development duration"""
        if system.start_date and system.end_date:
            duration = (system.end_date - system.start_date).days
            return {
                'total_days': duration,
                'weeks': duration // 7,
                'months': duration // 30
            }
        return None

    # Portfolio assessment helper methods
    def assess_code_quality(self, system):
        """Assess code quality for portfolio readiness (can enhance logic)"""
        # TODO: Logic Enhancement
        # Base score
        score = 50

        # GitHub Metrics
        if system.commit_count >= 50:
            score += 20
        elif system.commit_count >= 20:
            score += 10

        # Code size indicate effort
        if system.code_lines >= 1000:
            score += 15
        elif system.code_lines >= 500:
            score += 10

        # Documentation
        if system.description and len(system.description) > 200:
            score += 15

        return min(score, 100)

    def assess_feature_completeness(self, system):
        """Assess feature completeness (can enhance w GH issue tracking etc)"""
        # TODO: Logic Enhancement - API Integration
        feature_count = system.features.count()
        features_complete = system.features.filter(implementation_status='completed').count() if system.features else 0

        # Based on percent complete
        score = round(features_complete / feature_count * 100, 1) if feature_count else 0

        # Bonus for having features documented
        if feature_count >= 5:
            score += 20
        elif feature_count >= 3:
            score += 10

        return min(score, 100)

    def assess_documentation(self, system):
        """Assess documentation quality (can enhance)"""
        # TODO: Logic Enhancement
        score = 0

        # Has description
        if system.description:
            score += 30

        # Has setup instructions (later)
        # if system.setup_instructions:
        #     score += 25

        # Has usage examples (later)
        # if system.usage_examples:
        #     score += 25

        # For now, use other content fields
        # Has Technical Details
        if system.technical_details:
            score += 25

        # Has Challenges
        if system.challenges:
            score += 25

        # Has related DataLogs
        if system.get_related_logs().exists():
            score += 20

        return min(score, 100)

    def assess_tech_showcase(self, system):
        """Assess how well system showcases technical skills (can enhance)"""
        # TODO: Logic Enhancement
        # Base score
        score = 50

        # Number of technologies
        tech_count = system.technologies.count()
        if tech_count >= 5:
            score += 25
        elif tech_count >= 3:
            score += 15

        # Skills developed
        skills_count = system.skills_developed.count()
        if skills_count >= 5:
            score += 25
        elif skills_count >= 3:
            score += 15

        return min(score, 100)

    def assess_learning_evidence(self, system):
        """Assess evidence of learning progression (can enhance)"""
        # TODO: Logic Enhancement
        # Base score
        score = 40

        # Has learning documentation
        if system.has_learning_documentation():
            score += 25

        # Has milestones
        milestone_count = system.milestones.count()
        if milestone_count >= 3:
            score += 20
        elif milestone_count >= 1:
            score += 10

        # Has skill gains documented
        if system.skill_gains.exists():
            score += 15

        return min(score, 100)

    def assess_deployment(self, system):
        """Assess deployment/demo availability"""
        # Base score
        score = 30

        if system.live_url or system.demo_url:
            score += 40

        if system.github_url:
            score += 20

        if system.status == 'deployed':
            score += 10

        return min(score, 100)

    def get_portfolio_recommendations(self, system, criteria):
        """Generate portfolio improvement recommendations (can enhance)"""
        # TODO: Logic Enhancement
        recommendations = []

        for criterion in criteria:
            if criterion['score'] < 70:
                recommendations.append({
                    'area': criterion['name'],
                    'current_score': criterion['score'],
                    'suggestion': self.get_improvement_suggestion(criterion['name'], criterion['score']),
                    'priority': 'high' if criterion['score'] < 50 else 'medium'
                })

        return sorted(recommendations, key=lambda x: x['current_score'])[:4]

    def get_improvement_suggestion(self, area, score):
        """Get specific improvement suggestions (can enhance)"""
        suggestions = {
            "Code Quality": "Add more commits, improve documentation, refactor complex code",
            "Feature Completeness": "Complete remaining features, add more functionality",
            "Documentation": "Add comprehensive README, setup instructions, usage examples",
            "Technology Showcase": "Integrate additional relevant technologies",
            "Learning Evidence": "Document learning process, add milestones",
            "Deployment/Demo": "Deploy to live server, create demo video",
        }
        return suggestions.get(area, "Continue improving this area")

    # Additional helper methods - SIMPLIFIED - can enhance later
    def assess_documentation_completeness(self, system, related_logs):
        """Assess how well-documented learning process is"""
        return min(related_logs.count() * 20, 100)

    def get_tech_learning_context(self, tech, system):
        """Determine learning context for technology"""
        # Simple heuristic
        if system.learning_stage in ['tutorial', 'guided']:
            return 'first_time'
        elif system.learning_stage == 'independent':
            return 'building_on'
        else:
            return 'mastery'

    def assess_tech_mastery(self, tech, system):
        """Assess mastery level of technology in this project/system"""
        # Simplifed assessment
        if system.complexity >= 8:
            return 'advanced'
        elif system.complexity >= 5:
            return 'intermediate'
        else:
            return 'beginner'

    def assess_tech_learning_impact(self, tech, system):
        """Assess learning impact of using this tech"""
        # Simplfied metric
        return min(system.complexity * 2, 10)

    def extract_learning_challenges(self, feature):
        """Extract learning challenges from feature description - can integrate logic from performance-based view for keyword searches"""
        # Simplified - look for challenge keywords
        challenge_keywords = ['challenge', 'difficult', 'complex', 'new', 'first time', 'hard']
        challenges = []

        if feature.description:
            for keyword in challenge_keywords:
                if keyword in feature.description.lower():
                    challenges.append(keyword)

        return challenges

    def map_feature_to_skills(self, feature, system):
        """Map feature to skills developed - can enhance"""
        # Simplified mapping
        feature_skills = []
        for skill in system.skills_developed.all():
            if skill.name.lower() in feature.description.lower():
                feature_skills.append(skill)
        return feature_skills[:3]

    def assess_feature_complexity(self, feature):
        """Assess individual feature complexity - can enhance"""
        # Simplified assessment based on description length and keywords
        complexity_keywords = ['api', 'database', 'authentication', 'real-time', 'async', 'integration']
        # Base complexity
        score = 3

        if feature.description:
            score += min(len(feature.description) // 100, 3)
            for keyword in complexity_keywords:
                if keyword in feature.description.lower():
                    score += 1

        return min(score, 10)

    def get_implementation_insights(self, feature):
        """Extract implementation insights from feature - can enhance"""
        # Simplified - could be enhanced with NLP
        insights = []
        if feature.description and len(feature.description) > 100:
            insights.append("Detailed implementation documented")

        return insights

    def identify_feature_learning_moments(self, features_data):
        """Identify key learning moments from features"""
        learning_moments = []

        for feature_data in features_data:
            if feature_data['learning_challenges']:
                learning_moments.append({
                    'feature': feature_data['feature'].title,
                    'challenges': feature_data['learning_challenges'],
                    'skills': [s.name for s in feature_data['skills_applied']]
                })

        return learning_moments[:3]

    def get_dependency_learning_context(self, dependency):
        """Get learning context for dependency"""
        # Why was this dependency chosen? What did it teach?
        # This would be more for when I incorporate technology/skills into dependencies and purpose field
        # if dependency.purpose:
        #     return f"Learning {dependency.name} for {dependency.purpose}"
        return f"Integrating {dependency.depends_on} into system as type {dependency.dependency_type}"

    def assess_integration_complexity(self, dependency):
        """Assess complexity of integrating dependency - can enhance"""
        # Simplified assessment - could be enhanced
        if dependency.is_critical:
            return 8
        return 5

    def map_dependency_skills(self, dependency, system):
        """Map dependency to skills required/learned - can enhance"""
        # Simplified - for now return empty list
        return []

    def suggest_alternatives(self, dependency):
        """Suggest alternative dependencies - can enhance"""
        # Simplified return empty list - could be enhanced w alternative database
        return []


# ===================== GOLD STANDARD VIEWS - BEFORE LEARNING FOCUS REWORK =====================


class EnhancedSystemsDashboardView(TemplateView):
    """
    🚀 AURA Systems Command Center - The Ultimate Dashboard

    Using New Manager Methods
    """

    template_name = "projects/systems_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Use cache for expensive queries (5 min)
        cache_timeout = 300

        # Core dashboard stats using new manager
        dashboard_stats = cache.get('dashboard_stats_v2')
        if not dashboard_stats:
            dashboard_stats = self.get_dashboard_stats()
            cache.set('dashboard_stats_v2', dashboard_stats, cache_timeout)

        context['dashboard_stats'] = dashboard_stats

        # Featured systems using new manager methods
        context["featured_systems"] = SystemModule.objects.featured().deployed()[:6]

        # Recent systems activity using new manager methods
        context["recent_systems"] = SystemModule.objects.recently_updated(7)[:8]
        context['systems_in_development'] = SystemModule.objects.in_development()[:5]

        # Technology insights
        context['technology_insights'] = self.get_technology_insights()
        context['tech_usage_stats'] = context['technology_insights']['usage_stats']

        # Recent logs
        context["recent_logs"] = SystemLogEntry.objects.select_related(
            'system', 'post'
        ).order_by('-created_at')[:8]

        # Performance data for dashboard panels
        context['performance_data'] = self.get_performance_data()

        # System alerts
        context['system_alerts'] = self.get_system_alerts()

        # Systems by status for status panels
        context['systems_by_status'] = self.get_systems_by_status()

        # Chart for visualizations
        context['chart_data'] = self.get_chart_data()

        return context

    def get_dashboard_stats(self):
        """Enahnced dashboard stats using new manager methods."""

        # Use new dashboard_stats() method
        base_stats = SystemModule.objects.dashboard_stats()

        # Add performance-specific stats
        performance_systems = SystemModule.objects.with_performance_data()

        # Add development metrics
        all_systems = SystemModule.objects.all()

        enhanced_stats = {
            # Include all base stats from manager
            **base_stats,

            # Performance metrics
            'avg_uptime': performance_systems.aggregate(
                avg=Avg('uptime_percentage')
            )['avg'],

            'total_daily_users': performance_systems.aggregate(
                total=Sum('daily_users')
            )['total'] or 0,

            # Development metrics
            'total_code_lines': all_systems.aggregate(
                total=Sum('code_lines')
            )['total'] or 0,

            'total_commits': all_systems.aggregate(
                total=Sum('commit_count')
            )['total'] or 0,

            # New manager method stats
            'recently_updated_count': SystemModule.objects.recently_updated(7).count(),
            'high_priority_count': SystemModule.objects.high_priority().count(),

        }

        return enhanced_stats

    def get_technology_insights(self):
        """Technology usage analytics and trends."""
        # Top technologies by usage
        usage_stats = Technology.objects.annotate(
            usage_count=Count('systems', filter=Q(systems__status__in=['deployed', 'published']))
        ).filter(usage_count__gt=0).order_by('-usage_count')[:8]

        # Technology diversity score
        total_systems = SystemModule.objects.filter(status__in=['deployed', 'published']).count()
        unique_technologies = Technology.objects.filter(
            systems__status__in=['deployed', 'published']
        ).distinct().count()

        diversity_score = (unique_technologies / total_systems * 100) if total_systems > 0 else 0

        return {
            'usage_stats': usage_stats,
            'total_unique_technologies': unique_technologies,
            'diversity_score': round(diversity_score, 1),
        }

    def get_performance_data(self):
        """Performance metrics for dashboard panels."""
        # Get systems w performance data
        performing_systems = SystemModule.objects.with_performance_data()

        if not performing_systems.exists():
            return {
                'avg_performance': None,
                'avg_uptime': None,
                'health_distribution': {}
            }

        # Calculate averages
        avg_performance = performing_systems.aggregate(
            avg=Avg('performance_score')
        )['avg']

        avg_uptime = performing_systems.aggregate(
            avg=Avg('uptime_percentage')
        )['avg']

        # Health distribution using new model method
        health_distribution = SystemModule.get_health_distribution()

        return {
            "avg_performance": round(avg_performance, 1) if avg_performance else None,
            "avg_uptime": round(avg_uptime, 1) if avg_uptime else None,
            "health_distribution": health_distribution,
        }

    def get_system_alerts(self):
        """Generate alerts for alert panels."""
        alerts = []

        # Use new manager methods for cleaner queries
        low_performance_systems = SystemModule.objects.with_performance_data().filter(
            performance_score__lt=70
        )

        if low_performance_systems.exists():
            alerts.append(
                {
                    "icon": "tachometer-alt",
                    "title": "Performance Alert",
                    "message": f"{low_performance_systems.count()} system{'s' if low_performance_systems.count() > 1 else ''} showing low performance scores.",
                    "created_at": timezone.now(),
                    "level": "warning",
                }
            )

        # Check for stale development projects using new method, this is really only blanket checkc but can dial in later
        stale_systems = SystemModule.objects.in_development().recently_updated(30)
        if not stale_systems.exists():
            # If no recent updates, that means all dev systems are stale
            total_dev_systems = SystemModule.objects.in_development().count()
            if total_dev_systems > 0:
                alerts.append(
                    {
                        "icon": "schedule",
                        "title": "Stale Development",
                        "message": f"{total_dev_systems} systems not updated in 30+ days",
                        "created_at": timezone.now(),
                        "level": "info",
                    }
                )

        return alerts

    # May be able to eliminate as well and get from dashboard_stats() model method
    def get_systems_by_status(self):
        """
        Get systems count using new model methods.
        """
        return {
            'deployed': SystemModule.objects.deployed().count(),
            'published': SystemModule.objects.published().count(),
            'in_development': SystemModule.objects.in_development().count(),
            'featured': SystemModule.objects.featured().count()
        }

    def get_chart_data(self):
        """Data formatted for charts and visualizations (simplified)"""
        # Simple completion trend
        all_systems = SystemModule.objects.all()
        avg_completion = (
            all_systems.aggregate(avg=Avg("completion_percent"))["avg"] or 0
        )

        # Mock trend data - you can enhance this with real historical data
        completion_trend = [
            {"month": "Jan", "value": max(0, avg_completion - 15)},
            {"month": "Feb", "value": max(0, avg_completion - 10)},
            {"month": "Mar", "value": max(0, avg_completion - 5)},
            {"month": "Apr", "value": avg_completion},
        ]

        return {
            "completion_trend": completion_trend,
            "current_completion": avg_completion,
        }

# ===================== ENHANCED SYSTEM LIST VIEW =====================


class EnhancedSystemListView(ListView):
    """
    Enhanced System List using all new manager methods and model enhancements
    Features: Advanced filtering, search, performance analytics, unified container styling
    """

    model = SystemModule
    template_name = "projects/system_list.html"
    context_object_name = "systems"
    paginate_by = 12

    def get_queryset(self):
        """Enhanced filtered query using new manager methods w optimized queries."""
        # Start w optimized base query
        queryset = SystemModule.objects.select_related('system_type', 'author').prefetch_related('technologies', 'features')

        # Apply enhanced filters using new manager methods
        status_filter = self.request.GET.get('status')
        if status_filter == "deployed":
            queryset = queryset.deployed()
        elif status_filter == "published":
            queryset = queryset.published()
        elif status_filter == "in_development":
            queryset = queryset.in_development()
        elif status_filter == "featured":
            queryset = queryset.featured()
        elif status_filter == "recent":
            queryset = queryset.recently_updated(30)
        elif status_filter == "high_priority":
            queryset = queryset.high_priority()
        elif status_filter == "with_metrics":
            queryset = queryset.with_performance_data()

        # Technology filter
        tech_filter = self.request.GET.get("tech")
        if tech_filter:
            queryset = queryset.filter(technologies__slug=tech_filter)

        # System Type Filter
        type_filter = self.request.GET.get("type")
        if type_filter:
            queryset = queryset.filter(system_type__slug=type_filter)

        # Complexity filter
        complexity_filter = self.request.GET.get('complexity')
        if complexity_filter:
            queryset = queryset.filter(complexity=complexity_filter)

        # Performance filtering using enhanced fields
        min_performance = self.request.GET.get('min_performance')
        if min_performance:
            queryset = queryset.filter(performance_score__gte=min_performance)

        health_filter = self.request.GET.get('health')
        if health_filter:
            # This would require custom filtering logic for health status, can work on later
            pass

        # Search across enhanced fields
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(technical_details__icontains=search) |
                Q(technologies__name__icontains=search) |
                Q(features__title__icontains=search)
            ).distinct()

        # Enhanced Ordering
        order = self.request.GET.get("order", "recent")
        if order == "recent":
            queryset = queryset.order_by("-updated_at")
        elif order == "name":
            queryset = queryset.order_by("title")
        elif order == "completion":
            queryset = queryset.order_by("-completion_percent")
        elif order == "performance":
            queryset = queryset.order_by("-performance_score")
        elif order == "priority":
            queryset = queryset.order_by("-priority", "-updated_at")
        elif order == "complexity":
            queryset = queryset.order_by("-complexity")
        elif order == "status":
            queryset = queryset.order_by("status", "-updated_at")

        return queryset

    def get_context_data(self, **kwargs):
        """Enhanced context using new manager methods and dashboard stats."""
        context = super().get_context_data(**kwargs)

        # Use new dashboard_stats() method
        context['dashboard_stats'] = SystemModule.objects.dashboard_stats()

        # Enhanced filter data
        context.update({
            # Tecchnology stats using new methods
            'technologies': Technology.objects.annotate(
                usage_count=Count('systems', filter=Q(systems__status__in=['deployed', 'published']))
            ).filter(usage_count__gt=0).order_by('-usage_count')[:10],

            # System types w counts
            'system_types': SystemType.objects.annotate(
                usage_count=Count('systems')
            ).filter(usage_count__gt=0).order_by('-usage_count'),

            # Quick stats using new manager methods
            'quick_stats': {
                "featured_count": SystemModule.objects.featured().count(),
                "deployed_count": SystemModule.objects.deployed().count(),
                "in_development_count": SystemModule.objects.in_development().count(),
                "high_priority_count": SystemModule.objects.high_priority().count(),
                "with_performance_count": SystemModule.objects.with_performance_data().count(),
                "recently_updated_count": SystemModule.objects.recently_updated(7).count(),
            },

            # Performance analytics
            'performance_analytics': self.get_performance_analytics(),

            # Active filters for display
            'active_filters': self.get_active_filters(),

            # Pagination info
            'total_systems': self.get_queryset().count(),

            # Featured Systems for sidebar
            'featured_systems': SystemModule.objects.featured().deployed()[:4],
        })

        return context

    def get_performance_analytics(self):
        """Get performance analytics using enhanced model methods."""
        systems_with_performance = SystemModule.objects.with_performance_data()

        if not systems_with_performance.exists():
            return None

        return {
            'avg_performance': systems_with_performance.aggregate(
                avg=Avg('performance_score')
            )['avg'],
            'avg_uptime': systems_with_performance.aggregate(
                avg=Avg('uptime_percentage')
            )['avg'],
            'total_daily_users': systems_with_performance.aggregate(
                total=Sum('daily_users')
            )['total'] or 0,
            'performance_distribution': self.get_performance_distribution(),
        }

    def get_performance_distribution(self):
        """Get distribution of systems by performance score."""
        systems = SystemModule.objects.with_performance_data()

        distribution = {
            'excellent': systems.filter(performance_score__gte=90).count(),
            'good': systems.filter(performance_score__range=[70, 89]).count(),
            'fair': systems.filter(performance_score__range=[50, 69]).count(),
            'poor': systems.filter(performance_score__lt=50).count(),
        }

        return distribution

    def get_active_filters(self):
        """Get currently active filters for display."""
        filters = {}

        if self.request.GET.get('status'):
            filters['Status'] = self.request.GET.get('status').replace('_', '').title()

        if self.request.GET.get('tech'):
            try:
                tech = Technology.objects.get(slug=self.request.GET.get('tech'))
                filters['Technology'] = tech.name
            except:
                pass

        if self.request.GET.get('type'):
            try:
                sys_type = SystemType.objects.get(slug=self.request.GET.get('type'))
                filters['Type'] = sys_type.name
            except:
                pass

        if self.request.GET.get('complexity'):
            complexity_map = {
                1: 'Basic',
                2: 'Intermediate',
                3: 'Advanced',
                4: 'Complex',
                5: 'Enterprise'
            }
            complexity = int(self.request.GET.get('complexity'))
            filters['Complexity'] = complexity_map.get(complexity, 'Unknown')

        if self.request.GET.get('search'):
            filters['Search'] = self.request.GET.get('search')

        return filters

# ===================== ENHANCED SYSTEM DETAIL VIEW =====================


class SystemControlInterfaceView(DetailView):
    """
    System Control Interface - Nested System Command Center

    Like logging into a specific system's control panel with nested interfaces:
    - Main system overview dashboard
    - DataLogs control panel (nested view of related logs)
    - Technology stack analyzer
    - Performance monitoring console
    - Feature management interface
    - Development timeline viewer
    - Dependencies analyzer
    """

    model = SystemModule
    template_name = "projects/system_control_interface.html"
    context_object_name = "system"

    def get_queryset(self):
        """Optimized queryset for system control interface"""
        return SystemModule.objects.select_related(
            "system_type", "author"
        ).prefetch_related(
            "technologies",
            "features",
            "images",
            "metrics",
            "dependencies",
            "dependents",
            "log_entries__post",
            "log_entries__post__category",
            "log_entries__post__tags")

    def get_context_data(self, **kwargs):
        """Enhanced context for system control interface"""
        context = super().get_context_data(**kwargs)
        system = self.object

        # Get active control panel from URL parameter
        active_panel = self.request.GET.get('panel', 'overview')
        context['active_panel'] = active_panel

        # System metrics and dashboard data
        context.update({
            # Enhanced system metrics using model methods
            'system_metrics': system.get_dashboard_metrics(),
            'deployment_readiness': system.get_deployment_readiness(),
            'health_status': system.get_health_status(),

            # Performance analytics
            'performance_data': self.get_performance_analytics(system),

            # Related systems using enhanced manager methods
            'related_systems': SystemModule.objects.filter(technologies__in=system.technologies.all())
            .exclude(id=system.id)
            .distinct()[:6],

            # Similar systems by type and status
            'similar_systems': self.get_similar_systems(system),

            # Panel-specific context data
            'panel_data': self.get_panel_data(system, active_panel),

            # Navigation data for control interface
            'control_panels': self.get_control_panels(system),

            # Quick access data
            'quick_stats': self.get_quick_stats(system),

            # For System Info
            'system': system,
        })

        return context

    def get_performance_analytics(self, system):
        """Get detailed performance analytics for the system"""
        analytics = {
            'completion_score': system.completion_percent or 0,
            'complexity_rating': system.get_complexity_display(),
            'status_color': system.get_status_badge_color(),
            'progress_color': system.get_progress_color(),
        }

        # Add performance metrics if available
        if hasattr(system, 'performance_score') and system.performance_score:
            analytics.update({
                'performance_score': system.performance_score,
                'uptime_percentage': getattr(system, 'uptime_percecntage', None),
                'daily_users': getattr(system, 'daily_users', None),
                'response_time': getattr(system, 'response_time_ms', None),
            })

        return analytics

    def get_similar_systems(self, system):
        """Get similar systems using enhanced manager methods."""
        if system.status == 'deployed':
            return SystemModule.objects.deployed().filter(
                system_type=system.system_type
            ).exclude(id=system.id)[:4]
        elif system.status in ['in_development', 'testing']:
            return SystemModule.objects.in_development().filter(
                system_type=system.system_type
            ).exclude(id=system.id)[:4]
        else:
            return SystemModule.objects.filter(
                system_type=system.system_type
            ).exclude(id=system.id)[:4]

    def get_control_panels(self, system):
        """Define available control panels w dynamic counts."""
        panels = [
            {
                "id": "overview",
                "name": "System Overview",
                "icon": "tachometer-alt",
                "description": "Main system dashboard and metrics",
                "count": None,
                "color": "teal",
            },
            {
                "id": "details",
                "name": "System Details",
                "icon": "info-circle",
                "description": "Comprehensive system documentation and challenges",
                "count": None,
                "color": "navy",
            },
            {
                "id": "datalogs",
                "name": "DataLogs",
                "icon": "file-alt",
                "description": "Related development logs and documentation",
                "count": system.log_entries.count(),
                "color": "lavender",
            },
            {
                "id": "technologies",
                "name": "Tech Stack",
                "icon": "code",
                "description": "Technology analysis and dependencies",
                "count": system.technologies.count(),
                "color": "coral",
            },
            {
                "id": "features",
                "name": "Features",
                "icon": "puzzle-piece",
                "description": "System features and capabilities",
                "count": system.features.count() if hasattr(system, "features") else 0,
                "color": "mint",
            },
            {
                "id": "performance",
                "name": "Performance",
                "icon": "chart-line",
                "description": "Performance metrics and monitoring",
                "count": None,
                "color": "yellow",
            },
            {
                "id": "dependencies",
                "name": "Dependencies",
                "icon": "project-diagram",
                "description": "System dependencies and relationships",
                "count": system.dependencies.count()
                if hasattr(system, "dependencies")
                else 0,
                "color": "navy",
            },
            {
                "id": "timeline",
                "name": "Timeline",
                "icon": "history",
                "description": "Development timeline and milestones",
                "count": None,
                "color": "gunmetal",
            },
        ]

        return panels

    def get_panel_data(self, system, panel):
        """Get data specific to the active control panel."""
        if panel == 'details':
            return self.get_details_panel_data(system)
        elif panel == 'datalogs':
            return self.get_datalogs_panel_data(system)
        elif panel == 'technologies':
            return self.get_technologies_panel_data(system)
        elif panel == 'features':
            return self.get_features_panel_data(system)
        elif panel == 'performance':
            return self.get_performance_panel_data(system)
        elif panel == 'dependencies':
            return self.get_dependencies_panel_data(system)
        elif panel == "timeline":
            return self.get_timeline_panel_data(system)
        else:
            # Overview
            return self.get_overview_panel_data(system)

    def get_details_panel_data(self, system):
        """System details panel - conprehensive documentation."""
        # Get challenges related to DataLogs
        challenges_logs = []
        if system.challenges:
            # Search for DataLogs that might address challenges mentioned in challenges field
            challenges_keywords = self.extract_keywords_from_markdown(system.challenges)

            # Find posts that contain challenge-related keywords
            for keyword in challenges_keywords[:5]:  # Limit to top 5 keywords
                related_posts = system.log_entries.select_related('post').filter(
                    Q(post__title__icontains=keyword) |
                    Q(post__content__icontains=keyword) |
                    Q(post__excerpt__icontains=keyword)
                )[:3]
                for entry in related_posts:
                    if entry not in challenges_logs:
                        challenges_logs.append({
                            'log_entry': entry,
                            'keyword': keyword,
                            'relevance': 'addresses challenges'
                        })
        return {
            'has_description': bool(system.description),
            'has_technical_details': bool(system.technical_details),
            'has_challenges': bool(system.challenges),
            'description_content': system.rendered_content() if system.description else None,
            'technical_details_content': system.render_technical_details() if system.technical_details else None,
            'challenges_content': system.rendered_challenges() if system.challenges else None,
            'challenges_logs': challenges_logs,
            'content_stats': {
                'description_word_count': len(system.description.split()) if system.description else 0,
                'technical_word_count': len(system.technical_details.split()) if system.technical_details else 0,
                'challenges_word_count': len(system.challenges.split()) if system.challenges else 0,
            }
        }

    def get_overview_panel_data(self, system):
        """Main overview panel data."""
        return {
            'recent_activity': system.log_entries.select_related('post').order_by('-created_at')[:5],
            'key_technologies': system.technologies.all()[:6],
            'completion_breakdown': {
                'completed': system.completion_percent or 0,
                'remaining': 100 - (system.completion_percent or 0)
            },
            'status_info': {
                'current_status': system.get_status_display(),
                'status_color': system.get_status_badge_color(),
                'last_updated': system.updated_at,
            }
        }

    def get_datalogs_panel_data(self, system):
        """DataLogs control panel - nested interface for system logs."""
        # Get all related logs w full details
        log_entries = system.log_entries.select_related(
            'post', 'post__category', 'post__author'
        ).prefetch_related(
            'post__tags'
        ).order_by('-created_at')

        # Group logs by category
        logs_by_category = {}
        for entry in log_entries:
            category = entry.post.category.name if entry.post.category else 'Uncategorized'
            if category not in logs_by_category:
                logs_by_category[category] = []
            logs_by_category[category].append(entry)

        # Get log stats
        log_stats = {
            'total_logs': log_entries.count(),
            'categories_count': len(logs_by_category),
            'recent_logs': log_entries[:8],
            'logs_by_priority': {
                'high': log_entries.filter(priority__gte=3).count(),
                'medium': log_entries.filter(priority=2).count(),
                'low': log_entries.filter(priority=1).count(),
            }
        }

        return {
            'logs_by_category': logs_by_category,
            'log_stats': log_stats,
            'all_log_entries': log_entries,
            'connection_types': SystemLogEntry.objects.filter(
                system=system
            ).values_list('connection_type', flat=True).distinct()
        }

    def get_technologies_panel_data(self, system):
        """Technology stack analyzer panel."""
        technologies = system.technologies.all()

        # Analyze technology usage across similar systems
        tech_analysis = {}
        for tech in technologies:
            similar_systems = SystemModule.objects.filter(
                technologies=tech,
                system_type=system.system_type
            ).exclude(id=system.id)

            tech_analysis[tech.name] = {
                'technology': tech,
                'usage_in_similar': similar_systems.count(),
                'similar_systems': similar_systems[:3],
                'category': getattr(tech, 'category', 'Unknown'),
            }

        return {
            'technologies': technologies,
            'tech_analysis': tech_analysis,
            'tech_stats': {
                'total_technologies': technologies.count(),
                'categories': technologies.values_list('category', flat=True).distinct(),
                'primary_stack': technologies.filter(is_primary=True) if hasattr(technologies.first(), 'is_primary') else technologies[:3],
            }
        }

    def get_features_panel_data(self, system):
        """Enhanced Features management interface with smart content generation."""
        features_data = {'features': [], 'feature_stats': {}}

        if hasattr(system, 'features'):
            features = system.features.all()

            feature_stats = {
                'total_features': features.count(),
                'completed_features': features.filter(implementation_status='completed').count() if features else 0,
                'in_progress_features': features.filter(implementation_status='in_progress').count() if features else 0,
                'planned_features': features.filter(implementation_status='planned').count() if features else 0,
            }

            features_data = {
                "features": features,
                "feature_stats": feature_stats,
                "features_by_status": {
                    "completed": features.filter(implementation_status="completed"),
                    "in_progress": features.filter(implementation_status="in_progress"),
                    "planned": features.filter(implementation_status="planned"),
                }
                if features
                else {},
            }

        # Smart content generation for features_overview and future_enhancecments
        features_data.update({
            'features_overview_content': self.get_or_generate_features_overview(system, features_data),
            'future_enhancements_content': self.get_or_generate_future_enhancements(system, features_data),
            'has_custom_features_overview': bool(system.features_overview),
            'has_custom_future_enhancements': bool(system.future_enhancements),
        })

        return features_data

    def get_or_generate_features_overview(self, system, features_data):
        """Get features over or generate from related features."""
        if system.features_overview:
            # Use existing content
            return system.features_overview

        # Auto-generate from related features if available
        if features_data['features']:
            completed_features = features_data['features_by_status'].get('completed', [])
            in_progress_features = features_data['features_by_status'].get('in_progress', [])

            generated_content = f'### {system.title} Features\n\n'

            if completed_features:
                generated_content += '#### **Implemented Features**\n\n'
                for feature in completed_features[:5]:  # Limit to 5
                    generated_content += f'- **{feature.title}**: {feature.description[:100]}{"..." if len(feature.description) > 100 else ""}\n'
                    generated_content += "\n"
            if in_progress_features:
                generated_content += '#### **Features in Development**\n\n'
                for feature in in_progress_features[:3]:  # Limit to 3
                    generated_content += f'- **{feature.title}**: {feature.description[:100]}{"..." if len(feature.description) > 100 else ""}\n'
                    generated_content += "\n"

            generated_content += f"*Total features: {features_data['feature_stats']['total_features']} ({features_data['feature_stats']['completed_features']} completed)*"

            return generated_content

        # Fallback: Generate from system description or technologies
        if system.description:
            return f'## Key Capabilities\n\n{system.excerpt or 'This system provides essential functionality for the portfolio ecosystem.'}\n\n*Features documentation is being developed.**'

        return None

    def get_or_generate_future_enhancements(self, system, features_data):
        """Get future enhanccements or generate from planned features."""
        if system.future_enhancements:
            # Use existing content
            return system.future_enhancements

        # Auto-Generate from planned features
        if features_data['features']:
            planned_features = features_data['features_by_status'].get('planned', [])

            if planned_features:
                generated_content = f'## {system.title} Roadmap\n\n'
                generated_content += "### **Planned Enhancements**\n\n"

                for i, feature in enumerate(planned_features[:6], 1):  # Limit to 6
                    generated_content += f"{i}. **{feature.title}**\n"
                    generated_content += f"   {feature.description[:150]}{'...' if len(feature.description) > 150 else ''}\n\n"

                generated_content += "### **Development Priorities**\n\n"
                high_priority = [f for f in planned_features if hasattr(f, "priority") and f.priority >= 3]
                if high_priority:
                    generated_content += "**High Priority:**\n"
                    for feature in high_priority[:3]:
                        generated_content += f"- {feature.title}\n"
                else:
                    generated_content += "Priorities are being evaluated based on user feedback and technical requirements.\n"

                return generated_content

        # Fallback: Generate generic roadmap
        if system.status in ["in_development", "testing"]:
            return f"## Development Roadmap\n\n### **Current Focus**\n\nCompleting core functionality and preparing for deployment.\n\n### 🎯 **Next Steps**\n\n- Performance optimization\n- Enhanced user experience\n- Additional feature development\n- Comprehensive testing\n\n*Detailed roadmap will be updated as development progresses.*"
        elif system.status == "deployed":
            return f"## Enhancement Roadmap\n\n### **Continuous Improvement**\n\nThis system is actively maintained with regular updates and enhancements.\n\n### 🎯 **Areas of Focus**\n\n- Performance monitoring and optimization\n- Feature enhancement based on usage analytics\n- Security updates and improvements\n- Integration with new technologies\n\n*Enhancement requests are evaluated based on user feedback and technical feasibility.*"

        return None

    def extract_keywords_from_markdown(self, markdown_content):
        """Extract key terms from markdown content for finding related logs."""
        if not markdown_content:
            return []

        # Remove additional formatting
        text = re.sub(r"[#*`\[\]()_-]", " ", markdown_content)

        # Split into words and filter for meaningful terms
        words = text.lower().split()

        # Filter out common words and keep technical terms
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'was', 'are', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}

        keywords = [word for word in words if len(word) > 3 and word not in stopwords]

        # Count frequency and return top keywords
        word_counts = Counter(keywords)

        return [word for word, count in word_counts.most_common(10)]

    def get_performance_panel_data(self, system):
        """Performance monitoring controls."""
        performance_data = {
            'has_performance_data': hasattr(system, 'performance_score') and system.performance_score,
            'current_metrics': {},
            'performance_history': [],
            'benchmarks': {}
        }

        if performance_data['has_performance_data']:
            performance_data['current_metrics'] = {
                'performance_score': system.performance_score,
                'uptime': getattr(system, 'uptime_percentage', None),
                'daily_users': getattr(system, 'daily_users', None),
                'response_time': getattr(system, 'response_time_ms', None),
            }

            # Mock performance history
            # TODO: Replace w real data
            performance_data['performance_history'] = [
                {'date': '2024-01-01', 'performance': 85, 'uptime': 99.2},
                {'date': '2024-01-02', 'performance': 88, 'uptime': 99.5},
                {'date': '2024-01-03', 'performance': 92, 'uptime': 99.8},
            ]

        return performance_data

    def get_dependencies_panel_data(self, system):
        """Dependencies and relationship analyzer."""
        dependencies_data = {
            'dependencies': [],
            'dependents': [],
            'dependency_graph': {},
            'risk_analysis': {}
        }

        if hasattr(system, 'dependencies'):
            dependencies_data['dependencies'] = system.dependencies.select_related('depends_on').all()

        if hasattr(system, 'dependents'):
            dependencies_data['dependents'] = system.dependents.select_related('system').all()

        return dependencies_data

    def get_timeline_panel_data(self, system):
        """Development timeline and milestones."""
        timeline_events = []

        # Add system creation
        timeline_events.append({
            'date': system.created_at,
            'event': 'System Created',
            'type': 'milestone',
            'description': f'System {system.title} was created'
        })

        # Add related log entries as timeline events
        for log_entry in system.log_entries.select_related('post').order_by('created_at'):
            timeline_events.append({
                'date': log_entry.created_at,
                'event': log_entry.post.title,
                'type': 'log',
                'description': log_entry.post.excerpt or 'Development log entry',
                'url': log_entry.post.get_absolute_url()
            })

        # Sort timeline by date
        timeline_events.sort(key=lambda x: x['date'], reverse=True)

        return {
            'timeline_events': timeline_events[:20],  # Limit to recent events
            'milestones': [event for event in timeline_events if event['type'] == 'milestone'],
            'development_logs': [event for event in timeline_events if event['type'] == 'log'],
        }

    def get_quick_stats(self, system):
        """Quick access stats for the system interface."""
        return {
            'completion_percent': system.completion_percent or 0,
            'technologies_count': system.technologies.count(),
            'logs_count': system.log_entries.count(),
            'days_since_update': (timezone.now().date() - system.updated_at.date()).days,
            'status_display': system.get_status_display(),
            'complexity_level': system.get_complexity_display(),
        }


# ===================== ENHANCED SYSTEM TYPE VIEWS =====================

class SystemTypeOverviewView(ListView):
    """
    Global System Type Overview - Shows all systems grouped by type
    This view renders when no specific system type is selected
    """
    model = SystemType
    template_name = "projects/system_type_overview.html"
    context_object_name = "system_types"

    def get_queryset(self):
        return SystemType.objects.prefetch_related(
            "systems__technologies"
        ).annotate(
            systems_count=Count('systems', filter=Q(systems__status='published')),
            deployed_count=Count('systems', filter=Q(systems__status='deployed')),
            avg_completion=Avg('systems__completion_percent')
        ).order_by('display_order')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Global stats using enhanced manager methods
        all_systems = SystemModule.objects.all()

        context.update({
            'page_title': 'System Types Overview',
            'total_systems': all_systems.count(),
            'total_deployed': all_systems.deployed().count(),
            'total_featured': all_systems.featured().count(),
            'total_in_development': all_systems.in_development().count(),

            # Performance distribution
            'performance_distribution': self.get_performance_distribution(),

            # Technology distribution across all types
            'top_technologies': Technology.objects.annotate(
                systems_count=Count('systems', filter=Q(systems__status__in=['deployed', 'published']))
            ).order_by('-systems_count')[:8],

            # Recent activity
            'recently_updated': all_systems.recently_updated(7).select_related('system_type')[:5],

            # Type analytics
            'type_analytics': self.get_type_analytics(),
        })

        return context

    def get_performance_distribution(self):
        """Get performance score distribution across all systems."""
        systems = SystemModule.objects.with_performance_data()

        return {
            'excellent': systems.filter(performance_score__gte=90).count(),
            'good': systems.filter(performance_score__range=[70, 89]).count(),
            'fair': systems.filter(performance_score__range=[50, 69]).count(),
            'poor': systems.filter(performance_score__lt=50).count(),
        }

    def get_type_analytics(self):
        """Get analytics for each system type."""
        type_data = []

        for system_type in self.get_queryset():
            type_systems = SystemModule.objects.filter(system_type=system_type)

            # Calculate health score based on deployment ratio and completion
            deployed_ratio = type_systems.deployed().count() / max(type_systems.count(), 1)
            avg_completion = type_systems.aggregate(avg=Avg('completion_percent'))['avg'] or 0
            health_score = (deployed_ratio * 50) + (avg_completion * 0.5)

            type_data.append({
                'type': system_type,
                'systems_count': type_systems.count(),
                'deployed_count': type_systems.deployed().count(),
                'featured_count': type_systems.featured().count(),
                'avg_completion': avg_completion,
                'health_score': min(100, health_score),
                'top_technologies': Technology.objects.filter(
                    systems__system_type=system_type
                ).annotate(
                    count=Count('systems')
                ).order_by('-count')[:3]
            })









# ===================== ENHANCED FEATURE VIEWS =====================


class FeaturedSystemsView(ListView):
    """Featured systems using new manager methods."""

    template_name = "projects/featured_systems.html"
    context_object_name = "systems"

    def get_queryset(self):
        # Use new featured() method
        return SystemModule.objects.featured().select_related("system_type")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Stats using new manager methods
        context.update(
            {
                "total_featured": SystemModule.objects.featured().count(),
                "featured_deployed": SystemModule.objects.featured().deployed().count(),
                "featured_in_dev": SystemModule.objects.featured()
                .in_development()
                .count(),
            }
        )

        return context


# ===================== TECHNOLOGY AND TYPE VIEWS =====================


class SystemTypeDetailView(DetailView):
    """Enhanced system type view using new manager methods."""

    model = SystemType
    template_name = "projects/system_type.html"
    context_object_name = "system_type"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        system_type = self.object

        # Systems in this type using new manager methods
        context["systems"] = SystemModule.objects.filter(
            system_type=system_type
        ).deployed()  # Use our new deployed() method

        # Stats using new manager methods
        type_systems = SystemModule.objects.filter(system_type=system_type)
        context.update(
            {
                "total_systems": type_systems.count(),
                "deployed_systems": type_systems.deployed().count(),
                "featured_systems": type_systems.featured().count(),
                "avg_completion": type_systems.aggregate(avg=Avg("completion_percent"))[
                    "avg"
                ]
                or 0,
            }
        )

        return context


class TechnologyDetailView(DetailView):
    """Enhanced technology view using new manager methods."""

    model = Technology
    template_name = "projects/technology_detail.html"
    context_object_name = "technology"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        technology = self.object

        # Systems using this tech - use new manager methods
        tech_systems = SystemModule.objects.filter(technologies=technology)
        context["systems"] = tech_systems.deployed()  # Only show deployed

        # Stats using new manager methods
        context.update(
            {
                "total_systems": tech_systems.count(),
                "deployed_systems": tech_systems.deployed().count(),
                "featured_systems": tech_systems.featured().count(),
                "in_development": tech_systems.in_development().count(),
            }
        )

        return context


# ===================== API ENDPOINTS =====================

@require_http_methods(["GET"])
def dashboard_api(request):
    """API endpoint for real-time dashboard updates using new manager methods."""

    # Get fresh stats using our dashboard_stats() method
    stats = SystemModule.objects.dashboard_stats()

    # Add real-time metrics
    recent_activity = SystemModule.objects.recently_updated(1).count()  # Last 24 hours
    high_priority_count = SystemModule.objects.high_priority().count()

    # Health distribution
    health_distribution = SystemModule.get_health_distribution()

    return JsonResponse(
        {
            "stats": stats,
            "recent_activity_count": recent_activity,
            "high_priority_count": high_priority_count,
            "health_distribution": health_distribution,
            "timestamp": timezone.now().isoformat(),
        }
    )

# ===================== ADMIN/MANAGEMENT VIEWS (AS-IS WILL NEED UPDATING WHEN USE) =====================


class SystemModuleCreateView(LoginRequiredMixin, CreateView):
    """Create a new system module."""

    model = SystemModule
    template_name = "projects/admin/system_form.html"
    fields = [
        "title",
        "subtitle",
        "system_type",
        "description",
        "features_overview",
        "technical_details",
        "complexity",
        "priority",
        "status",
        "featured",
        "technologies",
        "github_url",
        "live_url",
        "demo_url",
        "thumbnail",
        "banner_image",
        "start_date",
        "end_date",
    ]

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(
            self.request, f"System '{form.instance.title}' created successfully!"
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create New System"
        context["submit_text"] = "Create System"
        return context


class SystemModuleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing system module."""

    model = SystemModule
    template_name = "projects/admin/system_form.html"
    fields = [
        "title",
        "subtitle",
        "system_type",
        "description",
        "features_overview",
        "technical_details",
        "challenges",
        "future_enhancements",
        "complexity",
        "priority",
        "status",
        "featured",
        "technologies",
        "github_url",
        "live_url",
        "demo_url",
        "documentation_url",
        "completion_percent",
        "performance_score",
        "uptime_percentage",
        "thumbnail",
        "banner_image",
        "featured_image",
        "architecture_diagram",
        "start_date",
        "end_date",
        "deployment_date",
    ]

    def test_func(self):
        system = self.get_object()
        return self.request.user == system.author or self.request.user.is_staff

    def form_valid(self, form):
        messages.success(
            self.request, f"System '{form.instance.title}' updated successfully!"
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Edit System: {self.object.title}"
        context["submit_text"] = "Update System"
        return context


class SystemModuleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a system module."""

    model = SystemModule
    template_name = "projects/admin/system_confirm_delete.html"
    success_url = reverse_lazy("projects:system_list")

    def test_func(self):
        system = self.get_object()
        return self.request.user == system.author or self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        system = self.get_object()
        messages.success(request, f"System '{system.title}' deleted successfully!")
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Delete System: {self.object.title}"

        # Get related data that will be affected
        context["related_logs"] = self.object.get_related_logs()
        context["related_features"] = self.object.features.count()
        context["related_images"] = self.object.images.count()

        return context
