from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy, reverse

from django.db.models import Count, Avg, Q, Sum, Max, Min, F, Case, When, Value, IntegerField, CharField
from django.db.models.functions import TruncMonth, Extract, Coalesce
from django.http import JsonResponse
from django.utils import timezone
from django.core.cache import cache
from django.core.management import call_command

import re
from datetime import timedelta, datetime, date
import random
from collections import Counter, defaultdict
from io import StringIO
import json

from .models import SystemModule, SystemType, Technology, SystemFeature, SystemMetric, SystemDependency, SystemImage, SystemSkillGain, LearningMilestone, GitHubRepository, GitHubLanguage, GitHubCommitWeek, GitHubRepositoryManager
from core.services.github_api import GitHubAPIService, GitHubAPIError
from blog.models import Post, SystemLogEntry
from core.models import Skill, PortfolioAnalytics, SkillTechnologyRelation


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
    Learning-Focused System List - Updated to use real GitHub commit data
    instead of static sample data. Features:
    - Learning stage filtering (tutorial → independent → teaching)
    - Skills gained filtering and display
    - Portfolio readiness indicators
    - Time investment tracking
    - Real GitHub commit metrics and activity
    """

    model = SystemModule
    # template_name = "projects/system_list.html"  # Reuse existing template with learning context
    template_name = "projects/learning_system_list.html"  # Replace main system_list once cleaned up
    context_object_name = "systems"
    paginate_by = 12

    def get_queryset(self):
        """Enhanced query with learning-focused optimizations and real GitHub data"""
        # Start with optimized base query for learning data (exclude drafts, archived)
        queryset = (
            SystemModule.objects.exclude(status__in=["draft", "archived"])
            .select_related("system_type", "author")
            .prefetch_related(
                "technologies",
                "skills_developed",  # Important for learning cards
                "milestones",  # For recent achievements
                "skill_gains__skill",  # For skill gain details
                # NEW: GitHub Repository data w commit info
                "github_repositories",
                "github_repositories__languages",
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

        # GITHUB ACTIVITY FILTERING (NEW - using real commit data)
        activity_filter = self.request.GET.get("activity_level")
        if activity_filter:
            if activity_filter == "very_active":  # 20+ commits last 30 days
                queryset = queryset.filter(
                    github_repositories__commits_last_30_days__gte=20
                ).distinct()
            elif activity_filter == "active":  # 5+ commits last 30 days
                queryset = queryset.filter(
                    github_repositories__commits_last_30_days__gte=5
                ).distinct()
            elif activity_filter == "inactive":  # 0 commits last 30 days
                queryset = queryset.filter(
                    Q(github_repositories__commits_last_30_days=0)
                    | Q(github_repositories__isnull=True)
                ).distinct()

        # Search across learning-relevant fields
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(skills_developed__name__icontains=search)
                | Q(technologies__name__icontains=search)
            ).distinct()

        # SORTING OPTIONS WITH REAL GITHUB DATA
        order = self.request.GET.get("order", "recent_activity")

        if order == "learning_velocity":
            # Sort by skills gained per month (for enhanced sorting, could use
            # the enhanced_learning_velocity in post-processing, but for DB efficiency
            # we use skills count as proxy here)
            queryset = queryset.annotate(
                skills_count=Count("skills_developed")
            ).order_by("-skills_count")

        elif order == "github_activity":
            # Sort by recent GitHub activity (real data)
            queryset = queryset.order_by("-github_repositories__commits_last_30_days")

        elif order == "portfolio_readiness":
            # Sort by portfolio readiness first, then by completion (enhanced scoring available)
            queryset = queryset.order_by("-portfolio_ready", "-completion_percent")

        elif order == "complexity_evolution":
            # Sort by complexity score (enhanced complexity calculation happens
            # in post-processing for each system, but base complexity used for DB sorting)
            queryset = queryset.order_by("-complexity")

        elif order == "time_investment":
            # Sort by actual development hours
            queryset = queryset.order_by("-actual_dev_hours")
        
        elif order == "name":
            # Sort by system name
            queryset = queryset.order_by('title', '-updated_at')
        
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
            queryset = queryset.annotate(stage_order=stage_order).order_by('-stage_order', '-updated_at')

        else:  # default: recent_activity
            # Sort by most recent GitHub activity or system updates
            queryset = queryset.order_by(
                "-github_repositories__last_commit_date", "-updated_at"
            )

        return queryset

    def get_context_data(self, **kwargs):
        """Enhanced context with learning metrics using real GitHub data"""
        context = super().get_context_data(**kwargs)

        # Add learning-focused sidebar data
        context.update(
            {
                "learning_stage_distribution": self.get_learning_stage_distribution(),
                
                # Filters lists and options
                "skills_filter_list": self.get_skills_filter_list(),
                "available_learning_stages": SystemModule.LEARNING_STAGE_CHOICES,
                "available_filters": self.get_current_filters(),
                "active_filters": self.get_active_learning_filters(),
                "learning_stage_filters": self.get_learning_filter_options(),
                "github_activity": self.get_simple_github_distribution(),
                "tech_mastery": self.get_technology_mastery(),

                "skills_stats": self.get_skills_statistics(),
                "portfolio_stats": self.get_portfolio_readiness_stats(),
                "github_activity_stats": self.get_github_activity_stats(),  # NEW
                "time_investment_distribution": self.get_time_investment_distribution(),

                # Quick Stats for header
                'quick_stats': self.get_learning_quick_stats(),

                # NEW: Skill-tech insights
                'skill_tech_insights': self.get_skill_technology_insights(),
                'skill_tech_matrix_stats': self.get_skill_tech_matrix_summary(),
            }
        )

        # Enhance each system with real GitHub commit data for template
        for system in context['systems']:
            # Use ENHANCED methods instead of basic ones
            system.commit_stats = system.get_enhanced_commit_stats()  # NEW enhanced method
            system.github_activity_level = self.get_system_activity_level(system)
            system.real_complexity_score = system.get_complexity_evolution_score_with_github()  # NEW enhanced method
            
            # Add enhanced learning metrics for template use
            system.enhanced_learning_velocity = system.get_learning_velocity_with_github()
            system.enhanced_portfolio_readiness = system.get_portfolio_readiness_score_with_github()
            system.development_timeline = system.get_development_timeline_with_commits()
            system.learning_stage_color_with_activity = system.get_learning_stage_color_with_activity()

            # Skill summary for cards without GH data
            system.skill_summary = self.get_skill_summary(system)

            # NEW: Skill-technology relationship enhancements
            system = self.enhance_system_with_skill_tech_data(system)
        
        return context
    
    def get_skill_tech_matrix_summary(self):
        """NEW: Summary stats for skill-technology matrix"""
        
        total_skills = Skill.objects.count()
        total_technologies = Technology.objects.count()
        defined_relationships = SkillTechnologyRelation.objects.count()
        possible_relationships = total_skills * total_technologies

        return {
            'coverage_percentage': (defined_relationships / possible_relationships) * 100 if possible_relationships > 0 else 0,
            'total_skills': total_skills,
            'total_technologies': total_technologies,
            'defined_relationships': defined_relationships,
            'strong_relationships': SkillTechnologyRelation.objects.filter(strength__gte=3).count(),
            'primary_implementations': SkillTechnologyRelation.objects.filter(
                relationship_type='implementation'
            ).count()
        }
    
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
        
        if self.request.GET.get("activity_level"):
            activity_map = {
                "very_active": "Very Active (20+ Commits)",
                "active": "Active (5+ Commits)",
                "inactive": "Inactive (<5 Commits)",
            }
            filters["Activity Level"] = activity_map.get(
                self.request.GET.get("activity_level")
            )

        return filters
    
    def get_learning_filter_options(self):
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
    
    def get_skill_summary(self, system):
        """Get Skills development summary for system cards with no github data."""
        skill_summary = system.get_skill_development_summary()
        # See if new, improved, or mastered skills
        new_skills = skill_summary.get('new_skills', 0)
        improved_skills = skill_summary.get('improved_skills', 0)
        mastered_skills = skill_summary.get('mastered_skills', 0)
        prof_count = new_skills + improved_skills + mastered_skills

        return {
            'flags': {
                'has_skill_gains': bool(system.skill_gains),
                'has_proficiency': prof_count > 0,
                'has_milestones': bool(system.milestones),
            },
            'skill-proficiency': {
                'total_skills': skill_summary['total_skills'],
                'new_skills': skill_summary['new_skills'],
                'improved_skills': skill_summary['improved_skills'],
                'mastered_skills': skill_summary['mastered_skills'],
            },
            'milestones': {
                'total_milestones': system.milestones.count(),
                'major_milestones': system.milestones.filter(milestone_type__in=['first_time', 'breakthrough']).count(),
            }
        }

    def get_github_activity_stats(self):
        """Enhanced: Get GitHub activity distribution using enhanced commit data"""
        
        # Get all systems with GitHub repositories
        systems_with_repos = SystemModule.objects.filter(
            github_repositories__isnull=False
        ).distinct()
        
        if not systems_with_repos.exists():
            return {
                "total_systems": 0,
                "active_systems": 0,
                "activity_levels": []
            }

        # Count systems by enhanced activity level (using enhanced analysis)
        activity_counts = {'very_active': 0, 'active': 0, 'moderate': 0, 'low': 0, 'inactive': 0}
        
        for system in systems_with_repos:
            activity_level = self.get_system_activity_level(system)
            level = activity_level['level']
            if level in activity_counts:
                activity_counts[level] += 1

        return {
            "total_systems": systems_with_repos.count(),
            "active_systems": activity_counts['very_active'] + activity_counts['active'],
            "activity_levels": [
                {"level": "very_active", "count": activity_counts['very_active'], "color": "#4CAF50"},
                {"level": "active", "count": activity_counts['active'], "color": "#8BC34A"},
                {"level": "moderate", "count": activity_counts['moderate'], "color": "#FFC107"},
                {"level": "low", "count": activity_counts['low'], "color": "#FF9800"},
                {"level": "inactive", "count": activity_counts['inactive'], "color": "#9E9E9E"},
            ],
            # Adding simple counts for filter badges
            "very_active": activity_counts['very_active'],
            'active': activity_counts['active'],
            'moderate': activity_counts['moderate'],
            'low': activity_counts['low'],
            'inactive': activity_counts['inactive'],
            "activity_counts": activity_counts,
        }
    
    def get_simple_github_distribution(self):
        """
        Get counts of simple github activity for filter count badges.
        Can better integrate filter w get_github_activity_stats later.
        """
        all_systems = SystemModule.objects.exclude(status__in=['draft', 'archived'])
        if not all_systems.exists():
            return {
                'very_active': 0,
                'active': 0,
                'inactive': 0
            }
        
        very_active = all_systems.filter(github_repositories__commits_last_30_days__gte=20).count()
        active = all_systems.filter(github_repositories__commits_last_30_days__gte=5).count()
        inactive = all_systems.filter(
            Q(github_repositories__commits_last_30_days=0) |
            Q(github_repositories__isnull=True)).count()
        
        return {
            'very_active': very_active,
            'active': active,
            'inactive': inactive
        }

    def get_system_activity_level(self, system):
        """NEW: Calculate activity level using real GitHub data"""
        commit_stats = system.get_commit_stats()
        commits_30_days = commit_stats.get('commits_last_30_days', 0)
        
        # Consider weekly consistency for more nuanced activity levels
        weekly_analysis = commit_stats.get('weekly_analysis', {})
        consistency_score = weekly_analysis.get('consistency_score', 0)
        
        if commits_30_days >= 20 and consistency_score >= 60:
            return {'level': 'very_active', 'color': '#4CAF50', 'label': 'Very Active'}
        elif commits_30_days >= 20 or (commits_30_days >= 10 and consistency_score >= 70):
            return {'level': 'active', 'color': '#8BC34A', 'label': 'Active'}
        elif commits_30_days >= 5 or (commits_30_days >= 1 and consistency_score >= 50):
            return {'level': 'moderate', 'color': '#FFC107', 'label': 'Moderate'}
        elif commits_30_days >= 1:
            return {'level': 'low', 'color': '#FF9800', 'label': 'Low Activity'}
        else:
            return {'level': 'inactive', 'color': '#9E9E9E', 'label': 'Inactive'}

    # Using model method for enhanced complexity score
    # def calculate_real_complexity_score(self, system):
    #     """
    #     UPDATED: Calculate complexity score using real GitHub data
    #     instead of static sample data
    #     """
    #     commit_stats = system.get_commit_stats()

    #     # Base complexity from system attributes
    #     base_score = system.complexity or 5

    #     # Adjust based on real GitHub activity
    #     total_commits = commit_stats.get("total_commits", 0)
    #     repo_count = commit_stats.get("repository_count", 0)

    #     # Commit complexity factor (more commits = more complex)
    #     if total_commits >= 100:
    #         commit_factor = 3
    #     elif total_commits >= 50:
    #         commit_factor = 2
    #     elif total_commits >= 20:
    #         commit_factor = 1
    #     else:
    #         commit_factor = 0

    #     # Repository complexity factor (multiple repos = more complex)
    #     repo_factor = min(repo_count, 3)  # Cap at 3

    #     # Learning stage factor
    #     stage_factors = {
    #         "tutorial": 0,
    #         "guided": 1,
    #         "independent": 2,
    #         "refactoring": 3,
    #         "contributing": 4,
    #         "teaching": 5,
    #     }
    #     stage_factor = stage_factors.get(system.learning_stage, 2)

    #     # Calculate final score
    #     final_score = base_score + commit_factor + repo_factor + stage_factor

    #     return min(final_score, 15)  # Cap at 15

    def get_development_consistency(self, commit_stats):
        """Enhanced: Calculate development consistency using weekly data"""
        # Use weekly analysis if available (from enhanced commit stats)
        weekly_analysis = commit_stats.get('weekly_analysis', {})
        
        if weekly_analysis:
            consistency_score = weekly_analysis.get('consistency_score', 0)
            
            if consistency_score >= 80:
                return {'level': 'very_consistent', 'score': consistency_score, 'color': '#4CAF50'}
            elif consistency_score >= 60:
                return {'level': 'consistent', 'score': consistency_score, 'color': '#8BC34A'}
            elif consistency_score >= 40:
                return {'level': 'moderate', 'score': consistency_score, 'color': '#FFC107'}
            elif consistency_score >= 20:
                return {'level': 'inconsistent', 'score': consistency_score, 'color': '#FF9800'}
            else:
                return {'level': 'very_inconsistent', 'score': consistency_score, 'color': '#F44336'}
        
        # Fallback to basic calculation if weekly data not available
        commits_30_days = commit_stats.get('commits_last_30_days', 0)
        avg_commits_month = commit_stats.get('avg_commits_per_month', 0)
        
        if avg_commits_month > 0:
            consistency = min((commits_30_days / max(avg_commits_month, 1)) * 100, 100)
            
            if consistency >= 80:
                return {'level': 'consistent', 'score': consistency, 'color': '#4CAF50'}
            elif consistency >= 60:
                return {'level': 'moderate', 'score': consistency, 'color': '#FFC107'}
            else:
                return {'level': 'inconsistent', 'score': consistency, 'color': '#FF9800'}
        
        return {'level': 'no_data', 'score': 0, 'color': '#9E9E9E'}

    def calculate_development_span(self, commit_stats):
        """Enhanced: Calculate development span using enhanced GitHub data"""
        last_commit_date = commit_stats.get("last_commit_date")

        if not last_commit_date:
            return 0

        # Use weekly analysis data if available for more accurate span calculation
        weekly_analysis = commit_stats.get("weekly_analysis", {})
        if weekly_analysis:
            total_weeks = weekly_analysis.get("total_weeks_tracked", 0)
            active_weeks = weekly_analysis.get("active_weeks", 0)

            if total_weeks > 0:
                # Convert weeks to months
                estimated_months = total_weeks / 4.33  # Average weeks per month
                return round(estimated_months, 1)

        # Fallback to basic calculation
        total_commits = commit_stats.get("total_commits", 0)
        avg_per_month = commit_stats.get("avg_commits_per_month", 1)

        if avg_per_month > 0:
            estimated_months = total_commits / avg_per_month
            return round(estimated_months, 1)

        return 0

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
    
    def get_skills_filter_list(self):
        """Available skills for filtering"""
        return Skill.objects.filter(
            project_gains__isnull=False
        ).distinct().order_by('name')

    def get_portfolio_readiness_stats(self):
        """Portfolio readiness statistics"""
        all_systems = SystemModule.objects.exclude(status="draft")

        if not all_systems.exists():
            return {
                "ready_count": 0,
                "in_progress": 0,
                "total_count": 0,
                "ready_percentage": 0,
                "needs_work": [],
            }

        ready_count = all_systems.filter(portfolio_ready=True).count()
        in_progress_count = all_systems.filter(portfolio_ready=False).count()
        total_count = all_systems.count()

        return {
            "ready_count": ready_count,
            "in_progress": in_progress_count,
            "total_count": total_count,
            "ready_percentage": round((ready_count / total_count) * 100, 1),
            "needs_work": all_systems.filter(
                portfolio_ready=False, status__in=["deployed", "published"]
            )[:3],
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

    def get_time_investment_distribution(self):
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

    def get_current_filters(self):
        """Current filter values for template"""
        return {
            "learning_stage": self.request.GET.get("learning_stage", ""),
            "portfolio_ready": self.request.GET.get("portfolio_ready", ""),
            "skill": self.request.GET.get("skill", ""),
            "time_investment": self.request.GET.get("time_investment", ""),
            "activity_level": self.request.GET.get("activity_level", ""),  # NEW
            "technology": self.request.GET.get("technology", ""),
            "sort": self.request.GET.get("sort", "recent_activity"),
        }

    def get_learning_quick_stats(self):
        """Enhanced quick stats for header leveraging new skill-technology relationships"""
        from core.models import Skill, SkillTechnologyRelation

        # Exclude drafts, archived
        total_systems = SystemModule.objects.exclude(
            status__in=['draft', 'archived']
        ).count()

        # NEW: Enhanced Skills metrics using new skill-technology relationships
        unique_skills_applied = SystemSkillGain.objects.values('skill').distinct().count()
        unique_technologies_used = SystemSkillGain.objects.values('technologies_used').distinct().count()
        skill_tech_connections = SkillTechnologyRelation.objects.count()

        # NEW: Technology mastery indicators
        technologies_with_multiple_projects = SystemSkillGain.objects.values('technologies_used').annotate(
            system_count=Count('system', distinct=True)
        ).filter(system_count__gte=2).count()

        return {
            'total_systems': total_systems,
            'portfolio_ready_count': SystemModule.objects.filter(portfolio_ready=True).count(),

            # ENHANCED: Replace simple skills_gained_count with richer metrics
            # How many different skills practiced
            'unique_skills_applied': unique_skills_applied,
            # How many unique tech used
            'unique_technologies_used': unique_technologies_used,
            # How many skill-tech relationships defined
            'skill_tech_connections': skill_tech_connections,
            # Technologies used in 2+ projects
            'technologies_mastered': technologies_with_multiple_projects,


            'learning_stages_count': SystemModule.objects.values('learning_stage').distinct().count(),
            'recent_milestones_count': LearningMilestone.objects.filter(
                date_achieved__gte=timezone.now() - timezone.timedelta(days=30)
            ).count()
        }
    
    def get_skill_technology_insights(self):
        """NEW: Get insights about skill-technology relationships across all systems"""
        from core.models import SkillTechnologyRelation

        # Most common skill-tech pairings
        common_pairings = SkillTechnologyRelation.objects.values(
            'skill__name', 'technology__name'
        ).annotate(
            strength=Avg('strength'),
            usage_count=Count('id')
        ).order_by('-strength', '-usage_count')[:10]

        # Skills with most technology diversity
        skills_by_tech_diversity = SkillTechnologyRelation.objects.values(
            'skill__name'
        ).annotate(
            tech_count=Count('technology', distinct=True),
            avg_strength=Avg('strength')
        ).order_by('-tech_count')[:5]

        return {
            'common_pairings': common_pairings,
            'diverse_skills': skills_by_tech_diversity,
            'total_relationships': SkillTechnologyRelation.objects.count(),
            'strong_relationships': SkillTechnologyRelation.objects.filter(strength__gte=3).count()
        }
    
    def enhance_system_with_skill_tech_data(self, system):
        """NEW: Enhanced each system w skill-technology relationship data"""
        # Get unique skills applied in this system
        skills_applied = system.skill_gains.values('skill__name').distinct()

        # Get technologies used acorss all skill applications in this system
        technologies_used = system.skill_gains.values('technologies_used__name').distinct()

        # Calculate skill-technology alignment score for this system
        # High score = skills and technologies are well-matched according to SkillTechnologyRelation
        alignment_score = 0
        total_connections = 0

        for skill_gain in system.skill_gains.all():
            for tech in skill_gain.technologies_used.all():
                try:
                    relation = SkillTechnologyRelation.objects.get(
                        skill=skill_gain.skill,
                        technology=tech
                    )
                    alignment_score += relation.strength
                    total_connections += 1
                except SkillTechnologyRelation.DoesNotExist:
                    # Skill-tech pair used but not formally defined
                    total_connections += 1

        system.skill_tech_alignment = (alignment_score / total_connections) if total_connections > 0 else 0
        system.skills_applied_count = skills_applied.count()
        system.technologies_used_count = technologies_used.count()
        system.skill_tech_diversity_score = skills_applied.count() * technologies_used.count()

        return system

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
    Streamlined Learning System Control Interface - Clean HUD Design
    
    Focused on 5 core panels that showcase project portfolio effectively:
    - Overview: System metrics & GitHub activity 
    - Details: Project documentation & technical specs
    - Technologies: Tech stack with skill-technology relationships
    - DataLogs: Learning documentation 
    - Architecture: 3D diagrams & system visualization
    """

    model = SystemModule
    template_name = "projects/learning_system_control_interface.html"
    context_object_name = "system"

    def get_queryset(self):
        """Optimized queryset for streamlined panel data."""
        return SystemModule.objects.select_related(
            "system_type", "author"
        ).prefetch_related(
            "technologies",
            "skills_developed",
            "skill_gains__skill",
            "skill_gains__technologies_used",   # NEW: For skill-tech relationships
            "milestones", 
            "log_entries__post",  # DataLogs integration
            "log_entries__post__category",
            "log_entries__post__tags",
            "github_repositories",
            "github_repositories__languages",
            "architecture_components",
            "architecture_components__outgoing_connections",
            "architecture_components__incoming_connections",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        system = self.object

        # Get active panel from URL parameter
        active_panel = self.request.GET.get('panel', 'overview')

        # Architecture Diagram Integration
        context.update({
            'has_architecture': system.has_architecture_diagram(),
            'architecture_diagram': system.get_architecture_diagram() if system.has_architecture_diagram() else None,
        })

        # Streamlined control panels (5 instead of 8)
        context["control_panels"] = [
            {
                "id": "overview",
                "name": "System Overview",
                "icon": "tachometer-alt",
                "description": "System metrics, GitHub activity, and key performance indicators",
                "count": None,
            },
            {
                "id": "details",
                "name": "System Details",
                "icon": "file-alt",
                "description": "Technical documentation, setup instructions, and project specifications",
                "count": None,
            },
            {
                "id": "technologies",
                "name": "Tech Stack",
                "icon": "layer-group",
                "description": "Technologies used and skill-technology relationships",
                "count": system.technologies.count(),
            },
            {
                "id": "datalogs",
                "name": "DataLogs",
                "icon": "book-open",
                "description": "DataLog entries documenting development and learning",
                "count": system.log_entries.count(),
            },
            {
                "id": "architecture",
                "name": "Architecture",
                "icon": "project-diagram", 
                "description": "System architecture diagrams and component visualization",
                "count": system.architecture_components.count() if system.has_architecture_diagram() else None,
            },
        ]

    
        # Set Active panel and generate panel-specific data
        context['active_panel'] = active_panel
        context['panel_data'] = self.get_panel_data(system, active_panel)

        return context

    def get_panel_data(self, system, panel_type):
        """Generate data for each specific panel"""

        if panel_type == "overview":
            return self.get_overview_panel_data(system)
        elif panel_type == "details":
            return self.get_details_panel_data(system)
        elif panel_type == "datalogs":
            return self.get_datalogs_panel_data(system)
        elif panel_type == "technologies":
            return self.get_technologies_panel_data(system)
        elif panel_type == "architecture":
            return self.get_architecture_panel_data(system)
        else:
            return self.get_overview_panel_data(system)

    # Panel 1 - System Overview
    def get_overview_panel_data(self, system):
        """Enhanced overview panel with skill-technology insights."""

        # GitHub integration
        commit_stats = system.get_enhanced_commit_stats() if hasattr(system, 'get_enhanced_commit_stats') else {
            'total_commits': 0,
            'last_commit_date': None,
            'commits_last_30_days': 0,
            'weekly_analysis': {
                'recent_trend': {
                    'direction': 'stable',
                    'percentage': 0
                }
            }
        }

        # NEW: Skill-tech alignment for this system
        skill_tech_alignment = self.calculate_skill_tech_alignment(system)

        return {
            'system_metrics': {
                'status': system.get_status_display(),
                'status_color': system.get_status_badge_color(),
                'completion_percent': float(system.completion_percent),
                'complexity': system.complexity,
                'portfolio_ready': system.portfolio_ready,
                'learning_stage': system.get_learning_stage_display(),
                'time_invested': system.actual_dev_hours or system.estimated_dev_hours,
            },
            'github_stats': commit_stats,
            'skill_tech_stats': {
                'alignment_score': skill_tech_alignment['score'],
                'total_connections': skill_tech_alignment['connections'],
                'strong_connections': skill_tech_alignment['strong_connections'],
                'skill_diversity': skill_tech_alignment['skill_diversity'],
            },
            'learning_metrics': {
                'skills_gained': system.skill_gains.count(),
                'milestones_achieved': system.milestones.count(),
                'documentation_entries': system.log_entries.count(),
                'technologies_used': system.technologies.count(),
            },
            'quick_links': {
                'linked_repositories': system.github_repositories.all()[:3],
                'github_url': system.github_url,
                'live_url': system.live_url or system.demo_url,
                'documentation_url': system.documentation_url,
            }
        }
    
    def calculate_skill_tech_alignment(self, system):
        """Calculate how well skills and technologies align in this system."""
        skill_gains = system.skill_gains.prefetch_related('skill', 'technologies_used')

        total_connections = 0
        alignment_score = 0
        strong_connections = 0
        skills_used = set()

        for gain in skill_gains:
            skills_used.add(gain.skill.id)
            for tech in gain.technologies_used.all():
                total_connections += 1
                try:
                    relation = SkillTechnologyRelation.objects.get(
                        skill=gain.skill,
                        technology=tech
                    )
                    alignment_score += relation.strength
                    if relation.strength >= 3:
                        strong_connections += 1
                except SkillTechnologyRelation.DoesNotExist:
                    # Undefined relationship - neutral score
                    alignment_score += 2
        
        return {
            'score': (alignment_score / total_connections) if total_connections > 0 else 0,
            'connections': total_connections,
            'strong_connections': strong_connections,
            'skill_diversity': len(skills_used),
        }

    # Panel 2 - System Details
    def get_details_panel_data(self, system):
        """Project details and documentation"""
        return {
            'descriptions': {
                'main_description': system.description,
                'brief_description': system.excerpt,
                # 'technical_details': getattr(system, 'technical_details', None),
                # Leaving bc might add setup and usage - (updating to use existing tech details and features overview content fields)
                'setup_instructions': getattr(system, 'technical_details', None),
                'usage_examples': getattr(system, 'features_overview', None),
            },
            'project_info': {
                'system_type': system.system_type.name,
                'created_date': system.created_at,
                'last_updated': system.updated_at,
                'development_duration': self.calculate_dev_duration(system),
            },
        }
    
    # Panel 3 - Tech-Skills
    def get_technologies_panel_data(self, system):
        """Enhanced technologies panel w skills relationships."""
        technologies = system.technologies.all()

        # NEW: Get skill-tech relationships for this system
        tech_relationships = []
        for tech in technologies:
            # Find skills that use this technology in this system
            related_skills = system.skill_gains.filter(
                technologies_used=tech
            ).select_related('skill')

            skill_connections = []
            for skill_gain in related_skills:
                try:
                    relation = SkillTechnologyRelation.objects.get(
                        skill=skill_gain.skill,
                        technology=tech
                    )
                    skill_connections.append({
                        'skill': skill_gain.skill,
                        'relationship_type': relation.get_relationship_type_display(),
                        'strength': relation.strength,
                        'notes': relation.notes,
                    })
                except SkillTechnologyRelation.DoesNotExist:
                    skill_connections.append({
                        'skill': skill_gain.skill,
                        'relationship_type': 'Applied in Project',
                        'strength': 2,
                        'notes': 'Used in this project',
                    })
            
            tech_relationships.append({
                'technology': tech,
                'skill_connections': skill_connections,
                'connection_count': len(skill_connections),
            })

        return {
            'technologies': technologies,
            'tech_relationships': tech_relationships,
            'total_technologies': technologies.count(),
            'primary_language': self.get_primary_language(system),
            'tech_stack_summary': self.get_tech_stack_summary(technologies),
        }

    # Panel 4 - DataLogs Panel
    def get_datalogs_panel_data(self, system):
        """DataLogs integration"""
        log_entries = system.log_entries.select_related(
            'post', 'post__category'
        ).prefetch_related('post__tags')[:10]

        return {
            'log_entries': log_entries,
            'total_entries': system.log_entries.count(),
            'entry_types': self.get_log_entry_types(log_entries),
            'recent_entries': log_entries[:5],
        }
    
    # Panel 5 - Architecture Panel
    def get_architecture_panel_data(self, system):
        """Architecture visualization panel."""
        # incoming = system.architecture_components.incoming_connections
        # outgoing = system.architecture_components.outgoing_connections

        
        return {
            'has_architecture': system.has_architecture_diagram(),
            'components': system.architecture_components.all(),
            # 'incoming_connections': incoming,
            # 'outgoing_connections': outgoing,
            'component_count': system.architecture_components.count(),
            'core_components_count': system.architecture_components.filter(is_core=True).count(),
            # 'connection_count': incoming + outgoing,
            'architecture_complexity': self.calculate_architecture_complexity(system),
        }
    
    # Helper Methods for streamlined 5-panel view
    def calculate_dev_duration(self, system):
        """Calcualte development duration."""
        if system.start_date and system.end_date:
            return (system.end_date - system.start_date).days
        return None
    
    def get_primary_language(self, system):
        """Get primary programming language."""
        # TODO: Can be enhanced to use GitHubLanguage model stats
        languages = system.technologies.filter(category='language')
        return languages.first() if languages.exists() else None

    def get_tech_stack_summary(self, technologies):
        """Generate tech stack summary by category."""
        # TODO: Think I can rework a model method for this data
        summary = {}
        for tech in technologies:
            category = tech.get_category_display()
            if category not in summary:
                summary[category] = []
            summary[category].append(tech)
        return summary
    
    def get_log_entry_types(self, log_entries):
        """Get breakdown of log entry types."""
        types = {}
        for entry in log_entries:
            entry_type = entry.get_connection_type_display()
            types[entry_type] = types.get(entry_type, 0) + 1
        return types

    def calculate_architecture_complexity(self, system):
        """Calculate architecture complexity score."""
        # TODO: Can enhance if I like this metric
        if not system.has_architecture_diagram():
            return 0
        
        components = system.architecture_components.count()
        # connections = system.architecture_connections.count()

        # # Simple complexity calculation
        # return min(components + (connections * 0.5), 10)
        return min(components, 10)

    # ======= FROM OLD VIEW from here down to end of view class
    # Only keeping here for now in case I want to preserve charts 
    # Panel to combine Skills and Tech
    def get_skills_tech_analysis_data(self, system):
        """
        Combined Skills & Technology Analysis Panel with Plotly Charts
        Uses SkillsTechChartsService to generate interactive visualizations
        """
        from .services.skills_tech_charts_service import SkillsTechChartsService
    
        # Initialize the charts service
        charts_service = SkillsTechChartsService(system)

        # ==================== SKILLS DATA ====================
        skills_data = []
        
        # Get skills for this system with progression data
        skill_gains = system.skill_gains.select_related('skill').all()
        
        for skill_gain in skill_gains:
            skill = skill_gain.skill
            
            # Skill data for display
            skills_data.append({
                'skill': skill,
                'proficiency_gained': skill_gain.proficiency_gained,
                'proficiency_display': skill_gain.get_proficiency_gained_display(),
                'learning_context': skill_gain.how_learned,
                'other_projects': skill.project_gains.exclude(system=system).select_related('system')[:3],
                'mastery_level': skill.get_mastery_level(),
                'is_new_skill': skill_gain.proficiency_gained <= 2,
                'color': getattr(skill, 'color', 'teal')
            })
        
        # ==================== TECHNOLOGY DATA ====================
        tech_data = []
        
        # Get technologies for this system with usage analysis
        technologies = system.technologies.all()
        
        for tech in technologies:
            mastery_level = self.assess_tech_mastery(tech, system)
            learning_context = self.get_tech_learning_context(tech, system)
            
            # Technology data for display
            tech_data.append({
                'technology': tech,
                'mastery_level': mastery_level,
                'mastery_numeric': self.get_mastery_numeric(mastery_level),
                'learning_context': learning_context,
                'related_skills': system.skills_developed.filter(name__icontains=tech.name),
                'other_projects': tech.systems.exclude(id=system.id)[:3],
                'usage_count': tech.systems.count(),
                'is_primary_tech': learning_context in ['core_framework', 'primary_language'],
                'color': getattr(tech, 'color', 'coral')
            })
        
        # ==================== RELATIONSHIPS DATA ====================
        # Find connections between skills and technologies
        skill_tech_connections = []
        
        for skill_gain in skill_gains:
            skill = skill_gain.skill
            related_techs = []
            
            # Find technologies that relate to this skill
            for tech in technologies:
                if (skill.name.lower() in tech.name.lower() or 
                    tech.name.lower() in skill.name.lower() or
                    self.check_skill_tech_relationship(skill, tech)):
                    related_techs.append(tech)
            
            if related_techs:
                skill_tech_connections.append({
                    'skill': skill,
                    'technologies': related_techs,
                    'connection_strength': len(related_techs),
                    'proficiency': skill_gain.proficiency_gained
                })
        
        # ==================== SUMMARY METRICS ====================
        analysis_summary = {
            'total_skills': len(skills_data),
            'new_skills_count': len([s for s in skills_data if s['is_new_skill']]),
            'advanced_skills_count': len([s for s in skills_data if s['proficiency_gained'] >= 4]),
            'total_technologies': len(tech_data),
            'primary_tech_count': len([t for t in tech_data if t['is_primary_tech']]),
            'skill_tech_connections': len(skill_tech_connections),
            'avg_proficiency': sum(s['proficiency_gained'] for s in skills_data) / len(skills_data) if skills_data else 0,
            'mastery_distribution': {
                'beginner': len([s for s in skills_data if s['proficiency_gained'] <= 2]),
                'intermediate': len([s for s in skills_data if s['proficiency_gained'] == 3]),
                'advanced': len([s for s in skills_data if s['proficiency_gained'] >= 4])
            }
        }
        
        # ==================== GENERATE PLOTLY CHARTS ====================
        # Generate the interactive charts using our service
        skills_radar_html = charts_service.generate_skills_radar_chart()
        tech_donut_html = charts_service.generate_tech_donut_chart()
        skill_tech_network_html = charts_service.generate_skill_tech_network()
        # tech_sunburst_html = charts_service.generate_tech_sunburst_chart()
        # learning_sunburst_html = charts_service.generate_learning_journey_sunburst()
        
        return {
            # Display data
            'skills_data': skills_data,
            'tech_data': tech_data, 
            'skill_tech_connections': skill_tech_connections,
            'analysis_summary': analysis_summary,
            
            # Plotly chart HTML (ready to embed)
            'skills_radar_chart': skills_radar_html,
            'tech_donut_chart': tech_donut_html,
            'skill_tech_network_chart': skill_tech_network_html,
            # 'tech_sunburst_chart': tech_sunburst_html,
            # 'learning_sunburst_chart': learning_sunburst_html,
            
            # Chart availability flags
            'has_skills_chart': bool(skills_data),
            'has_tech_chart': bool(tech_data),
            'has_network_chart': bool(skills_data and tech_data),
        }
    
    # Helper methods combined skill/tech view
    def get_mastery_numeric(self, mastery_level):
        """Convert mastery level to numeric for charts"""
        mapping = {
            'beginner': 1,
            'intermediate': 2, 
            'advanced': 3,
            'expert': 4
        }
        return mapping.get(mastery_level, 1)

    def assess_tech_mastery(self, tech, system):
        """Assess mastery level of technology in this system"""
        # You can enhance this logic based on your existing implementation
        total_systems = tech.systems.count()
        if total_systems >= 3:
            return 'advanced'
        elif total_systems >= 2:
            return 'intermediate'
        else:
            return 'beginner'

    def get_tech_learning_context(self, tech, system):
        """Get the learning context for this technology"""
        tech_name_lower = tech.name.lower()
        
        if any(framework in tech_name_lower for framework in ['django', 'react', 'flask', 'vue']):
            return 'core_framework'
        elif any(lang in tech_name_lower for lang in ['python', 'javascript', 'java', 'c++']):
            return 'primary_language'  
        elif any(frontend in tech_name_lower for frontend in ['html', 'css', 'bootstrap', 'tailwind']):
            return 'frontend_essential'
        elif any(tool in tech_name_lower for tool in ['git', 'docker', 'postgresql', 'redis']):
            return 'supporting_tool'
        else:
            return 'experimental'
    
    def check_skill_tech_relationship(self, skill, tech):
        """Check if a skill and technology are related"""
        skill_name = skill.name.lower()
        tech_name = tech.name.lower()
        
        # Define relationship patterns
        relationships = {
            'python': ['django', 'flask', 'fastapi', 'pandas', 'numpy'],
            'javascript': ['react', 'vue', 'node', 'express', 'jquery'],
            'database': ['postgresql', 'mysql', 'sqlite', 'mongodb'],
            'frontend': ['html', 'css', 'bootstrap', 'tailwind', 'sass'],
            'version control': ['git', 'github', 'gitlab'],
            'api': ['rest', 'graphql', 'django', 'flask', 'fastapi']
        }
        
        # Check if skill relates to technology
        for skill_key, tech_list in relationships.items():
            if skill_key in skill_name:
                return any(t in tech_name for t in tech_list)
        
        # Check reverse relationship  
        for skill_key, tech_list in relationships.items():
            if any(t in tech_name for t in tech_list):
                return skill_key in skill_name
        
        return False

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

    def get_development_status(self, commit_stats):
        """Determine development status from commit data"""
        if not commit_stats["last_commit_date"]:
            return "No Development Tracked"

        days_since_commit = (timezone.now() - commit_stats["last_commit_date"]).days

        if days_since_commit <= 7:
            return "Active Development"
        elif days_since_commit <= 30:
            return "Recent Development"
        elif days_since_commit <= 90:
            return "Moderate Activity"
        else:
            return "Maintenance Mode"

    def get_activity_level(self, commits_30_days):
        """Get activity level description"""
        if commits_30_days >= 20:
            return "Very Active"
        elif commits_30_days >= 10:
            return "Active"
        elif commits_30_days >= 5:
            return "Moderate"
        elif commits_30_days >= 1:
            return "Light"
        else:
            return "Inactive"
    
    def get_development_consistency(self, commit_stats):
        """Rate development consistency"""
        if commit_stats["avg_commits_per_month"] >= 10:
            return 5  # Very consistent
        elif commit_stats["avg_commits_per_month"] >= 5:
            return 4  # Consistent
        elif commit_stats["avg_commits_per_month"] >= 2:
            return 3  # Moderate
        elif commit_stats["avg_commits_per_month"] >= 1:
            return 2  # Irregular
        else:
            return 1  # Inconsistent
    
    def calculate_development_span(self, commit_stats):
        """Calculate months of development activity"""
        if not commit_stats.get("last_commit_date"):
            return 0

        # Find earliest repo creation (approximation)
        earliest_date = commit_stats.get("last_commit_date")  # Fallback

        # Calculate months between earliest and latest activity
        months = max(1, (timezone.now() - earliest_date).days / 30)
        return round(months, 1)

    def analyze_learning_trajectory(self, system, commit_stats):
        """Analyze the learning trajectory"""
        trajectory = []

        # Code volume trajectory
        if commit_stats["total_commits"] > 50:
            trajectory.append("High Code Volume")
        elif commit_stats["total_commits"] > 20:
            trajectory.append("Moderate Code Volume")
        else:
            trajectory.append("Learning Focused")

        # Consistency trajectory
        if commit_stats["avg_commits_per_month"] > 5:
            trajectory.append("Consistent Development")
        else:
            trajectory.append("Project-Based Learning")

        # Skill development trajectory
        if system.skills_developed.count() >= 5:
            trajectory.append("Multi-Skill Development")
        elif system.skills_developed.count() >= 3:
            trajectory.append("Focused Skill Building")
        else:
            trajectory.append("Exploratory Learning")

        return trajectory

    def find_commits_around_date(self, system, target_date, days=7):
        """Find commits around a specific date"""
        if not target_date:
            return []

        start_date = target_date - timedelta(days=days)
        end_date = target_date + timedelta(days=days)

        related_commits = []
        for repo in system.github_repositories.all():
            if (
                repo.last_commit_date and start_date <= repo.last_commit_date <= end_date
            ):
                related_commits.append(
                    {
                        "repo_name": repo.name,
                        "commit_date": repo.last_commit_date,
                        "message": repo.last_commit_message,
                        "author": "sonnibytes",
                    }
                )

        return related_commits

    def analyze_development_patterns(self, timeline_events):
        """Analyze patterns in development timeline"""
        commit_events = [e for e in timeline_events if e["type"] == "commit"]
        milestone_events = [e for e in timeline_events if e["type"] == "milestone"]

        patterns = {
            "commit_frequency": len(commit_events),
            "milestone_frequency": len(milestone_events),
            "documentation_ratio": len(
                [e for e in timeline_events if e["type"] == "datalog"]
            )
            / max(1, len(commit_events)),
            "development_style": "Documentation-Driven"
            if len([e for e in timeline_events if e["type"] == "datalog"])
            > len(commit_events) / 2
            else "Code-First",
        }

        return patterns

    def get_commit_trend(self, commit_stats):
        """Determine commit trend direction"""
        if commit_stats["commits_last_30_days"] > commit_stats["avg_commits_per_month"]:
            return "increasing"
        elif (
            commit_stats["commits_last_30_days"] < commit_stats["avg_commits_per_month"] * 0.5
        ):
            return "decreasing"
        else:
            return "stable"

    def categorize_skills(self, skill_gains):
        """Categorize skills by type"""
        categories = {
            # Frameworks/db/system-level
            'infrastructure': [],
            # language, ml, api, data, all else
            'technical': [],
            # soft skills
            'soft': [],
            # tool, ai
            'tools': [],
        }

        category_map = {
            'language': 'technical',
            'framework': 'infrastructure',
            'tool': 'tools',
            'database': 'infrastructure',
            'soft_skill': 'soft',
            'api': 'technical',
            'data': 'technical',
            'system': 'infrastructure',
            'ml': 'technical',
            'ui': 'technical',
            'ai': 'tools',
            'other': 'technical'
        }

        for gain in skill_gains:
            category = gain.skill.category.lower() if gain.skill.category else 'technical'
            general_category = category_map.get(category, 'technical')
            categories[general_category].append(gain)

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
        """Assess code quality for portfolio readiness (can enhance logic)
        * Updated commits count w GH data
        """
        # TODO: Logic Enhancement
        commit_stats = system.get_commit_stats()

        # Base score
        score = 50

        # GitHub Metrics
        if commit_stats['total_commits'] >= 50:
            score += 20
        elif commit_stats["total_commits"] >= 20:
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


# ===================== ENHANCED TECHNOLOGY VIEWS =====================


class TechnologiesOverviewView(ListView):
    """
    Enhanced Technologies Overview - Streamlined glass-card design
    Shows skill-technology relationships and learning progression
    """
    model = Technology
    template_name = "projects/technologies_overview.html"
    context_object_name = "technologies"

    def get_queryset(self):
        """Get technologies w enhanced skill-relationship annotations."""
        return Technology.objects.annotate(
            # Learning focused metrics
            total_projects=Count('systems', distinct=True),
            completed_projects=Count('systems', filter=Q(systems__status__in=['deployed', 'published']), distinct=True),
            learning_projects=Count('systems', filter=Q(systems__status='in_development'), distinct=True),
            featured_projects=Count('systems', filter=Q(systems__featured=True), distinct=True),

            # Skill level based on project complexity
            skill_level=Avg('systems__complexity'),

            # NEW: Skill-Technology relationship count
            skill_connections=Count('skill_relations', distinct=True),
            strong_skill_connections=Count('skill_relations', filter=Q(skill_relations__strength__gte=3), distinct=True),
        ).filter(
            total_projects__gt=0  # Only show technologies actually used
        ).order_by('category', '-total_projects')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Learning journey overview stats
        all_systems = SystemModule.objects.all()
        all_technologies = self.get_queryset()

        # NEW: Skill-technology relationship insights
        skill_tech_relations = SkillTechnologyRelation.objects.all()

        context.update({
            'page_title': 'Technology Skills Overview',
            'page_subtitle': 'Learning progression across my development tech stack',
            'show_breadcrumbs': True,

            # Learning Journey Metrics
            'total_technologies_learned': all_technologies.count(),
            'total_projects_built': all_systems.count(),
            'technologies_in_progress': all_technologies.filter(learning_projects__gt=0).count(),
            'advanced_technologies': all_technologies.filter(skill_level__gte=4).count(),

            # NEW: Skill-technology relationship metrics
            'skill_tech_connecctions': skill_tech_relations.count(),
            'strong_relationships': skill_tech_relations.filter(strength__gte=3).count(),

            # Enhanced category navigation
            'technology_categories': self.get_enhanced_technology_categories(),

            # NEW: Learning insights w skill connections
            'learning_insights': self.get_skill_tech_learning_insights(),
        })

        return context
    
    def get_enhanced_technology_categories(self):
        """Get technology categories w skill relationship data"""
        categories = []

        for category_code, category_name in Technology.CATEGORY_CHOICES:
            category_techs = Technology.objects.filter(category=category_code)

            if category_techs.exists():
                # Calculate enhanced category metrics
                total_projects = SystemModule.objects.filter(
                    technologies__category=category_code
                ).distinct().count()

                # Avg skill level for this category
                avg_skill_level = category_techs.annotate(
                    avg_complexity=Avg('systems__complexity')
                ).aggregate(
                    overall_avg=Avg('avg_complexity')
                )['overall_avg'] or 0

                # NEW: Skill connections for this category
                skill_connections = SkillTechnologyRelation.objects.filter(
                    technology__category=category_code
                ).count()

                # Get sample technologies for display
                sample_technologies = category_techs.annotate(
                    project_count=Count('systems')
                ).order_by('-project_count')[:5]

                categories.append({
                    'code': category_code,
                    'name': category_name,
                    'color': self.get_category_color(category_code),
                    'icon': self.get_category_icon(category_code),
                    'tech_count': category_techs.count(),
                    'project_count': total_projects,
                    'skill_level': round(avg_skill_level, 1),
                    'skill_connections': skill_connections,
                    # For display in template
                    'technologies': sample_technologies,
                })

        return categories
    
    def get_skill_tech_learning_insights(self):
        """Generate learning insights incorporating skill-tech relationships"""
        insights = []

        # Most connected technology (has most skill relationships)
        most_connected_tech = Technology.objects.annotate(
            connection_count=Count('skill_relations')
        ).order_by('-connection_count').first()

        if most_connected_tech and most_connected_tech.connection_count > 0:
            insights.append({
                'type': 'most_connected',
                'title': f'Most Versatile: {most_connected_tech.name}',
                'description': f'Connected to {most_connected_tech.connection_count} different skill areas',
                'icon': 'network-wired',
                'color': 'teal'
            })
        
        # Strongest skill-tech relationship
        strongest_relation = SkillTechnologyRelation.objects.select_related(
            'skill', 'technology'
        ).order_by('-strength').first()

        if strongest_relation:
            insights.append({
                'type': 'strongest_connection',
                'title': f'{strongest_relation.skill.name} + {strongest_relation.technology.name}',
                'description': f'Strongest skill-technology combination (strength {strongest_relation.strength}/4)',
                'icon': 'star',
                'color': 'lavender'
            })
        
        # Most recent technology w skill development
        newest_skill_tech = SkillTechnologyRelation.objects.select_related(
            'skill', 'technology'
        ).order_by('-created_at').first()

        if newest_skill_tech:
            insights.append({
                'type': 'latest_connection',
                'title': f'Latest Connection: {newest_skill_tech.technology.name}',
                'description': f'Recently connected to {newest_skill_tech.skill.name}',
                'icon': 'seedling',
                'color': 'mint'
            })
        
        return insights
    
    # def get_technology_categories(self):
    #     """Get technology categories w stats - like category hexagons"""
    #     categories = []

    #     for category_code, category_name in Technology.CATEGORY_CHOICES:
    #         category_techs = Technology.objects.filter(category=category_code)
    #         if category_techs.exists():
    #             # Calculate category learning metrics
    #             total_projects = SystemModule.objects.filter(
    #                 technologies__category=category_code
    #             ).distinct().count()

    #             avg_skill_level = category_techs.annotate(
    #                 avg_complexity=Avg('systems__complexity')
    #             ).aggregate(
    #                 overall_avg=Avg('avg_complexity')
    #             )['overall_avg'] or 0

    #             categories.append({
    #                 'code': category_code,
    #                 'name': category_name,
    #                 'color': self.get_category_color(category_code),
    #                 'icon': self.get_category_icon(category_code),
    #                 'tech_count': category_techs.count(),
    #                 'project_count': total_projects,
    #                 'skill_level': round(avg_skill_level, 1),
    #             })
    #     return categories
    
    def get_category_color(self, category):
        """Get color for each technology category."""
        colors = {
            "language": "#ff8a80",  # Coral for languages
            "framework": "#b39ddb",  # Lavender for frameworks
            "database": "#26c6da",  # Teal for databases
            "cloud": "#fff59d",  # Yellow for cloud
            "tool": "#a5d6a7",  # Mint for tools
            "os": "#ffb6c1",  # Light pink for os
            "ai": "#20b2aa",  # Light sea green for ai
            "other": "#90a4ae",  # Gunmetal for other
        }
        return colors.get(category, "#90a4ae")
    
    def get_category_icon(self, category):
        """Get icon for each tech category."""
        icons = {
            "language": "code",
            "framework": "layer-group",
            "database": "database",
            "cloud": "cloud",
            "tool": "tools",
            "os": "gears",
            "ai": "brain",
            "other": "cube",
        }
        return icons.get(category, "cube")
    
    def get_learning_insights(self):
        """Generate learning progression insights."""
        insights = []

        # Find most used technology
        top_tech = Technology.objects.annotate(
            project_count=Count('systems')
        ).order_by('-project_count').first()

        if top_tech:
            insights.append({
                'type': 'primary_skill',
                'title': f'Primary Technology: {top_tech.name}',
                'description': f'Used in {top_tech.project_count} projects',
                'icon': 'star',
                'color': 'teal'
            })
        
        # Find newest technology (most recent project)
        newest_tech = Technology.objects.filter(
            systems__isnull=False
        ).annotate(
            latest_project=Max('systems__created_at')
        ).order_by('-latest_project').first()

        if newest_tech:
            insights.append({
                'type': 'latest_learning',
                'title': f'Latest Skill: {newest_tech.name}',
                'description': 'Most recently explored technology',
                'icon': 'seedling',
                'color': 'mint'
            })

        # Find complexity progression
        advanced_count = Technology.objects.annotate(
            avg_complexity=Avg('systems__complexity')
        ).filter(avg_complexity__gte=4).count()

        if advanced_count > 0:
            insights.append({
                'type': 'skill_growth',
                'title': f'{advanced_count} Advanced Technologies',
                'description': 'Demonstrating progression to complex implementations',
                'icon': 'chart-line',
                'color': 'lavender'
            })
        return insights


class TechnologyDetailView(DetailView):
    """
    Enhanced Technology Detail - Streamlined glass-card design
    Shows skill connections, learning timeline, and related projects
    """

    model = Technology
    template_name = "projects/technology_detail.html"
    context_object_name = "technology"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        technology = self.object

        # Get systems using this technology w enhanced data (Chronological for learning progression)
        tech_systems = SystemModule.objects.filter(technologies=technology).select_related(
            'system_type', 'author'
        ).prefetch_related('technologies', 'skills_developed').order_by('created_at')

        context.update({
            'page_title': f'{technology.name} - Learning Journey',
            'page_subtitle': f'Projects and skill development with {technology.name}',
            'show_breadcrumbs': True,

            # Basic metrics
            'total_projects': tech_systems.count(),
            'completed_projects': tech_systems.filter(status__in=['deployed', 'published']).count(),
            'learning_projects': tech_systems.filter(status='in_development').count(),
            'featured_projects': tech_systems.filter(featured=True).count(),

            # NEW: Skill-technology relationship data
            'skill_connections': self.get_skill_connections(technology),
            'skill_connections_count': technology.skill_relations.count(),

            # Enhanced progression metrics
            'skill_progression': self.get_enhanced_skill_progression(tech_systems, technology),
            'learning_timeline': self.get_enhanced_learning_timeline(tech_systems, technology),
            'complexity_progression': self.get_complexity_progression(tech_systems),

            # Systems using this technology
            'systems': tech_systems,

            # Related content
            'related_datalogs': self.get_related_datalogs(technology),
            'similar_technologies': self.get_similar_technologies(technology),
        })

        return context
    
    def get_skill_connections(self, technology):
        """Get skill-technology relationships for this tech"""
        return SkillTechnologyRelation.objects.filter(
            technology=technology
        ).select_related('skill').order_by('-strength', 'skill__name')
    
    def get_enhanced_skill_progression(self, systems, technology):
        """Calculate skill progression incorporating skill-tech relationships"""
        if not systems.exists():
            return {'current_level': 0, 'progression_data': []}
        
        # Calculate skill level based on project complexity and skill relationships
        avg_complexity = systems.aggregate(avg=Avg('complexity'))['avg'] or 1

        # Boost score based on number of strong skill connections
        strong_connections = technology.skill_relations.filter(strength__gte=3).count()
        skill_boost = min(strong_connections * 0.2, 1.0)  # Max boost of 1 pt

        current_level = min(avg_complexity + skill_boost, 5.0)

        # Create progression timeline
        progression_data = []
        for system in systems:
            progression_data.append({
                'date': system.created_at,
                'project': system.title,
                'complexity': system.complexity,
                'skills_gained': system.skills_developed.count(),
            })
        
        if current_level >= 4:
            level_display = 'Advanced'
        elif current_level >= 3:
            level_display = 'Intermediate'
        elif current_level >= 2:
            level_display = 'Learning'
        else:
            level_display = 'Beginner'
        
        return {
            'current_level': current_level,
            'level_display': level_display,
            'progression_data': progression_data,
            'skill_boost': skill_boost,
            'strong_connections': strong_connections,
        }
    
    # def get_skill_progression(self, systems):
    #     """Calculate skill level progression w this technology."""
    #     if not systems.exists():
    #         return {'level': 'Beginner', 'description': 'Getting started'}
        
    #     avg_complexity = systems.aggregate(avg=Avg('complexity'))['avg'] or 1
    #     project_count = systems.count()
    #     completion_rate = (systems.filter(
    #         status__in=['deployed', 'published']
    #     ).count() / project_count) * 100 if project_count > 0 else 0

    #     # Determine skill level based on complexity and experience
    #     if avg_complexity >= 4 and project_count >= 3:
    #         level = 'Advanced'
    #         description = f'Confident with complex implementation ({project_count} projects)'
    #     elif avg_complexity >= 3 and project_count >= 2:
    #         level = 'Intermediate'
    #         description = f'Growing proficiency through practice ({project_count} projects)'
    #     else:
    #         level = 'Learning'
    #         description = f'Building foundational skills ({project_count} project{"s" if project_count > 1 else ""})'
    #     return {
    #         'level': level,
    #         'description': description,
    #         'avg_complexity': round(avg_complexity, 1),
    #         'project_count': project_count,
    #         'completion_rate': round(completion_rate, 1),
    #     }
    
    def get_enhanced_learning_timeline(self, systems, technology):
        """Create enhanced learning timeline with skill milestones."""
        timeline = []

        # Add system milestones
        for system in systems:
            timeline.append({
                'date': system.created_at.date(),
                'title': f'Built {system.title}',
                'description': f'Applied {technology.name} in a {system.system_type.name.lower()} project',
                'type': 'project',
                'complexity': system.complexity,
                'url': system.get_absolute_url(),
            })
        
        # NEW: Add skill connections and milestones
        skill_connections = technology.skill_relations.all()
        for connection in skill_connections:
            if connection.first_used_together:
                timeline.append({
                    'date': connection.first_used_together,
                    'title': f'Connected to {connection.skill.name}',
                    'description': f'First applied {technology.name} for {connection.skill.name} ({connection.get_relationship_type_display().lower()})',
                    'type': 'skill_connection',
                    'strength': connection.strength,
                })
        
        # Sort by date and return
        timeline.sort(key=lambda x: x['date'])
        return timeline

    # def get_learning_timeline(self, systems):
    #     """Create a learning timeline for this technology."""
    #     timeline_items = []

    #     for system in systems.order_by('created_at'):
    #         timeline_items.append({
    #             'date': system.created_at,
    #             'title': system.title,
    #             'type': 'project',
    #             'complexity': system.complexity,
    #             'status': system.status,
    #             'description': system.excerpt or f'{system.get_complexity_display()} {system.system_type.name if system.system_type else "project"}',
    #             'url': system.get_absolute_url(),
    #         })
    #     return timeline_items
    
    def get_complexity_progression(self, systems):
        """Calculate complexity progression over time."""
        if not systems.exists():
            return {'avg_complexity': 0, 'progression': []}
        
        complexities = list(systems.values_list('complexity', flat=True))

        return {
            'avg_complexity': sum(complexities) / len(complexities),
            'min_complexity': min(complexities),
            'max_complexity': max(complexities),
            'progression': complexities,  # Ordered by creation date
            'growth': max(complexities) - min(complexities) if len(complexities) > 1 else 0,
        }
    
    def get_related_datalogs(self, technology):
        """Get DataLogs related to this technology."""
        try:
            from blog.models import Post

            # Search for posts that mention this tech
            related_posts = Post.objects.filter(
                Q(title__icontains=technology.name) |
                Q(content__icontains=technology.name) |
                Q(tags__name__icontains=technology.name)
            ).filter(status='published').distinct()[:6]

            return related_posts
        except ImportError:
            return []
    
    def get_similar_technologies(self, technology):
        """Get similar technologies (same category, excluding current)."""
        return Technology.objects.filter(
            category=technology.category
        ).exclude(id=technology.id).annotate(
            project_count=Count('systems'),
            # Skill level based on project complexity
            skill_level=Avg('systems__complexity'),
            # Skill-Tech relationship count
            skill_connections=Count('skill_relations', distinct=True)
            ).filter(project_count__gt=0)[:8]


# ===================== ENHANCED SYSTEM TYPE VIEWS =====================


class SystemTypesOverviewView(ListView):
    """
    System Types Overview - Shows all system types with learning progression
    Similar to technologies overview but focused on project types/categories
    """
    model = SystemType
    template_name = "projects/system_types_overview.html"
    context_object_name = "system_types"

    def get_queryset(self):
        """Get system types w learning-focused annotations."""
        return SystemType.objects.annotate(
            # Learning-focused metrics for each system type
            total_systems=Count('systems'),
            completed_systems=Count('systems', filter=Q(systems__status__in=['deployed', 'published'])),
            learning_systems=Count('systems', filter=Q(systems__status='in_development')),
            featured_systems=Count('systems', filter=Q(systems__featured=True)),
            avg_completion=Avg('systems__completion_percent'),
            avg_complexity=Avg('systems__complexity'),  # Avg complexity as skill progression indicator
            latest_project=Max('systems__created_at'),  # Most recent work in this type
        ).filter(
            total_systems__gt=0  # Only show types w actual projects
        ).order_by('display_order', 'name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Learning journey overview stats
        all_systems = SystemModule.objects.all()
        all_types = SystemType.objects.filter(systems__isnull=False).distinct()

        context.update({
            'page_title': 'Project Types Overview',
            'page_subtitle': 'Exploring different types of systems and applications in my learning journey',
            'show_breadcrumbs': True,

            # Learning Journey Metrics
            'total_project_types': all_types.count(),
            'total_systems_built': all_systems.count(),
            'types_in_progress': all_types.filter(
                systems__status='in_development'
            ).distinct().count(),
            'advanced_project_types': all_types.annotate(
                avg_complexity=Avg('systems__complexity')
            ).filter(avg_complexity__gte=3.5).count(),

            # System type insights
            'type_insights': self.get_type_insights(),

            # Complexity progression across types
            'complexity_distribution': self.get_complexity_distribution(),
        })

        return context
    
    def get_type_insights(self):
        """Generate insights about project type progression."""
        insights = []

        # Find most developed project type
        top_type = SystemType.objects.annotate(
            system_count=Count('systems'),
            completion_avg=Avg('systems__completion_percent')
        ).filter(system_count__gt=0).order_by('-system_count', '-completion_avg').first()

        if top_type:
            insights.append({
                'type': 'primary_focus',
                'title': f'Primary Focus: {top_type.name}',
                'description': f'{top_type.system_count} projects built',
                'icon': top_type.icon if top_type.icon else 'fa-star',
                'color': 'teal'
            })
        
        # Find newest project type (most recent learning)
        newest_type = SystemType.objects.filter(
            systems__isnull=False
        ).annotate(latest_project=Max('systems__created_at')).order_by('-latest_project').first()

        if newest_type:
            insights.append({
                'type': 'latest_exploration',
                'title': f'Latest Exploration: {newest_type.name}',
                'description': 'Most recently explored project type',
                'icon': newest_type.icon if newest_type.icon else 'fa-seedling',
                'color': 'mint'
            })
        
        # Find most complex project type
        complex_type = SystemType.objects.annotate(
            avg_complexity=Avg('systems__complexity')
        ).filter(systems__isnull=False).order_by('-avg_complexity').first()

        if complex_type and complex_type.avg_complexity >= 3.5:
            insights.append({
                'type': 'advanced_work',
                'title': f'Advanced Work: {complex_type.name}',
                'description': f'Average Complexity: {complex_type.avg_complexity:.1f}/5',
                'icon': complex_type.icon if complex_type.icon else 'fa-chart-line',
                'color': 'lavender'
            })
        return insights
    
    def get_complexity_distribution(self):
        """Get complexity distribution across all project types."""
        distribution = {
            'basic': SystemModule.objects.filter(complexity__lte=2).count(),
            'intermediate': SystemModule.objects.filter(complexity=3).count(),
            'advanced': SystemModule.objects.filter(complexity__gte=4).count(),
        }

        total = sum(distribution.values())
        if total > 0:
            distribution['basic_percent'] = round((distribution['basic'] / total) * 100, 1)
            distribution['intermediate_percent'] = round((distribution['intermediate'] / total) * 100, 1)
            distribution['advanced_percent'] = round((distribution['advanced'] / total) * 100, 1)
        
        return distribution


class SystemTypeDetailView(DetailView):
    """
    Enhanced System Type Detail - Shows learning progression within this project type
    Similar to technology detail but focused on systems of a specific type
    """

    model = SystemType
    template_name = "projects/system_type.html"
    context_object_name = "system_type"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        system_type = self.object

        # Get systems of this type w learning focus
        type_systems = SystemModule.objects.filter(system_type=system_type).select_related(
            'author'
        ).prefetch_related('technologies')

        # Learning progressionL order by complexity and date to show growth
        context["systems"] = type_systems.order_by('complexity', 'created_at')

        # Learning focused stats (not enterprise metrics)
        context.update({
            'page_title': f'{system_type.name} - Project Portfolio',
            'page_subtitle': f'My learning journey building {system_type.name.lower()} systems',
            'show_breadcrumbs': True,

            # Learning Journey Stats
            'total_systems': type_systems.count(),
            'completed_systems': type_systems.filter(status__in=['deployed', 'published']).count(),
            'learning_systems': type_systems.filter(status='in_development').count(),
            'featured_systems': type_systems.filter(featured=True).count(),

            # Skill progression metrics
            'skill_progression': self.get_skill_progression(type_systems),
            'learning_timeline': self.get_learning_timeline(type_systems),
            'complexity_progression': self.get_complexity_progression(type_systems),
            'technology_usage': self.get_technology_usage(type_systems),

            # Related learning (DataLogs integration)
            'related_datalogs': self.get_related_datalogs(system_type),

            # System type context
            'similar_types': self.get_similar_types(system_type),
        })

        return context
    
    def get_skill_progression(self, systems):
        """Calculate skill level progression within this project type."""
        if not systems.exists():
            return {'level': 'Getting Started', 'description': 'Beginning exploration'}
        
        avg_complexity = systems.aggregate(avg=Avg('complexity'))['avg'] or 1
        project_count = systems.count()
        completion_rate = (systems.filter(
            status__in=['deployed', 'published']
        ).count() / project_count) * 100 if project_count > 0 else 0

        # Determine skill level based on complexity and experience
        if avg_complexity >= 4 and project_count >= 3:
            level = 'Advanced'
            description = f"Sophisticated {self.object.name.lower()} implementations ({project_count} projects)"
        elif avg_complexity >= 3 or project_count >= 2:
            level = "Intermediate"
            description = f"Growing expertise in {self.object.name.lower()} development ({project_count} projects)"
        else:
            level = "Learning"
            description = f"Building foundational {self.object.name.lower()} skills ({project_count} project{'s' if project_count > 1 else ''})"

        return {
            "level": level,
            "description": description,
            "avg_complexity": round(avg_complexity, 1),
            "project_count": project_count,
            "completion_rate": round(completion_rate, 1),
        }
    
    def get_learning_timeline(self, systems):
        """Create a learning timeline for this project type."""
        timeline_items = []

        for system in systems.order_by('created_at'):
            timeline_items.append({
                'date': system.created_at,
                'title': system.title,
                'type': 'project',
                'complexity': system.complexity,
                'status': system.status,
                'description': system.excerpt or f'{system.get_complexity_display()} {self.object.name.lower()} project',
                'url': system.get_absolute_url(),
                'technologies': list(system.technologies.all()[:3]),  # Top 3 technologies
            })
        return timeline_items
    
    def get_complexity_progression(self, systems):
        """Show how complexity has grown over time within this type."""
        progression = []
        
        for system in systems.order_by('created_at'):
            progression.append({
                'title': system.title,
                'complexity': system.complexity,
                'complexity_display': system.get_complexity_display(),
                'date': system.created_at,
                'completion': system.completion_percent,
                'featured': system.featured,
            })
        
        return progression
    
    def get_technology_usage(self, systems):
        """Get technology usage stats within this project type."""
        from collections import Counter
        
        # Get all technologies used in this project type
        tech_usage = Counter()
        for system in systems:
            for tech in system.technologies.all():
                tech_usage[tech] += 1
        
        # Convert to list with percentages
        total_systems = systems.count()
        usage_stats = []
        
        for tech, count in tech_usage.most_common():
            percentage = (count / total_systems) * 100 if total_systems > 0 else 0
            usage_stats.append({
                'technology': tech,
                'count': count,
                'percentage': round(percentage, 1),
            })
        
        return usage_stats[:8]  # Top 8 technologies
    
    def get_related_datalogs(self, system_type):
        """Find DataLogs related to this system type."""
        # Import here to avoid circular imports
        from blog.models import Post
        
        # Search for posts that mention this system type
        related_posts = Post.objects.filter(
            Q(title__icontains=system_type.name) |
            Q(content__icontains=system_type.name) |
            Q(tags__name__icontains=system_type.name)
        ).filter(status='published').distinct()[:5]
        
        return related_posts
    
    def get_similar_types(self, system_type):
        """Find other system types with similar complexity or technology usage."""
        # Get other system types with similar average complexity
        current_complexity = SystemModule.objects.filter(
            system_type=system_type
        ).aggregate(avg=Avg('complexity'))['avg'] or 0
        
        similar_types = SystemType.objects.exclude(
            id=system_type.id
        ).annotate(
            system_count=Count('systems'),
            avg_complexity=Avg('systems__complexity')
        ).filter(
            system_count__gt=0,
            avg_complexity__gte=current_complexity - 0.5,
            avg_complexity__lte=current_complexity + 0.5
        )[:4]
        
        return similar_types


# ===================== ENHANCED FEATURED SYSTEMS VIEW =====================


class FeaturedSystemsView(ListView):
    """
    Featured Systems Portfolio Showcase - Recruiter-focused presentation
    Highlights best projects with learning progression and skill demonstration
    """
    model = SystemModule
    template_name = "projects/featured_systems.html"
    context_object_name = "featured_systems"
    paginate_by = 12

    def get_queryset(self):
        """Get featured systems w learning progression focus."""
        # Get featured systems w optimized queries
        queryset = SystemModule.objects.featured().select_related("system_type", 'author').prefetch_related(
            'technologies', 'features'
        )

        # Apply sorting based on URL params
        sort_by = self.request.GET.get('sort', 'complexity')

        if sort_by == 'complexity':
            # Show learning progression: simple to complex
            queryset = queryset.order_by('complexity', 'created_at')
        elif sort_by == 'recent':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'completion':
            queryset = queryset.order_by('-completion_percent', '-created_at')
        elif sort_by == 'technology':
            # Group by primary technology
            queryset = queryset.order_by('system_type__name', 'complexity')
        else:
            # Default: complexity progression
            queryset = queryset.order_by('complexity', 'created_at')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all featured systems for analytics
        all_featured = SystemModule.objects.featured()

        # Stats using new manager methods
        context.update({
            'page_title': 'Featured Project Portfolio',
            'page_subtitle': 'Showcasing my best work and learning progression across 2+ years of development',

            # Learning Journey Portfolio Stats
            'portfolio_stats': self.get_portfolio_stats(all_featured),

            # Skill Progression Analysis
            'skill_progression': self.get_skill_progression_analysis(all_featured),

            # Technology Mastery Breakdown
            'technology_mastery': self.get_technology_mastery(all_featured),

            # Learning Journey Insights
            'learning_insights': self.get_learning_insights(all_featured),

            # Filter/Sort Options
            'current_sort': self.request.GET.get('sort', 'complexity'),
            'available_sorts': self.get_available_sorts(),

            # Complexity Distribution for Featured Projects
            'complexity_distribution': self.get_complexity_distribution(all_featured),
        })

        return context
    
    def get_portfolio_stats(self, featured_systems):
        """Get portfolio-level stats for featured projects."""
        if not featured_systems.exists():
            return {}
        
        return {
            'total_featured': featured_systems.count(),
            'completed_projects': featured_systems.filter(status__in=['deployed', 'published']).count(),
            'avg_complexity': round(featured_systems.aggregate(avg=Avg('complexity'))['avg'] or 0, 1),
            'technologies_used': featured_systems.values('technologies').distinct().count(),
            'avg_completion': round(featured_systems.aggregate(avg=Avg('completion_percent'))['avg'] or 0, 1),
            'project_types': featured_systems.values('system_type').distinct().count(),
            'development_span': self.get_development_span(featured_systems),
        }
    
    def get_development_span(self, systems):
        """Calculate timespan of featured projects development."""
        dates = systems.aggregate(
            earliest=Min('created_at'),
            latest=Max('created_at')
        )

        if dates['earliest'] and dates['latest']:
            span = dates['latest'] - dates['earliest']
            months = span.days // 30
            return f"{months} months" if months > 0 else "Recent work"
        
        return "Continuous Improvement"
    
    def get_skill_progression_analysis(self, featured_systems):
        """Analyze skill progression across featured projects."""
        if not featured_systems.exists():
            return {}
        
        # Complexity progression over time
        systems_by_date = featured_systems.order_by('created_at')
        
        progression = []
        for system in systems_by_date:
            progression.append({
                'title': system.title,
                'date': system.created_at,
                'complexity': system.complexity,
                'technologies': list(system.technologies.all()[:2]),  # Primary technologies
            })
        
        # Learning velocity (projects per complexity level)
        complexity_counts = featured_systems.values('complexity').annotate(
            count=Count('id')
        ).order_by('complexity')
        
        return {
            'progression_timeline': progression[:8],  # Recent 8 projects
            'complexity_evolution': list(complexity_counts),
            'skill_growth_indicators': self.get_skill_growth_indicators(featured_systems),
        }
    
    def get_skill_growth_indicators(self, systems):
        """Calculate indicators of learning and skill growth."""
        indicators = []
        
        # Complexity progression
        early_projects = systems.order_by('created_at')[:3]
        recent_projects = systems.order_by('-created_at')[:3]
        
        if early_projects.exists() and recent_projects.exists():
            early_avg = early_projects.aggregate(avg=Avg('complexity'))['avg'] or 0
            recent_avg = recent_projects.aggregate(avg=Avg('complexity'))['avg'] or 0
            
            if recent_avg > early_avg:
                improvement = round((recent_avg - early_avg), 1)
                indicators.append({
                    'type': 'complexity_growth',
                    'title': 'Complexity Progression',
                    'description': f'Average complexity increased by {improvement} points',
                    'icon': 'chart-line',
                    'color': 'mint'
                })
        
        # Technology diversity
        tech_count = systems.values('technologies').distinct().count()
        if tech_count >= 5:
            indicators.append({
                'type': 'tech_diversity',
                'title': 'Technology Breadth',
                'description': f'Demonstrated proficiency across {tech_count} technologies',
                'icon': 'layer-group',
                'color': 'coral'
            })
        
        # Project completion rate
        completion_rate = (systems.filter(
            status__in=['deployed', 'published']
        ).count() / systems.count()) * 100 if systems.count() > 0 else 0
        
        if completion_rate >= 80:
            indicators.append({
                'type': 'completion_rate',
                'title': 'High Completion Rate',
                'description': f'{completion_rate:.0f}% of featured projects completed',
                'icon': 'check-circle',
                'color': 'teal'
            })
        
        return indicators
    
    def get_technology_mastery(self, featured_systems):
        """Analyze technology usage and mastery across featured projects."""
        # Count technology usage
        tech_usage = Counter()
        tech_complexity = {}
        
        for system in featured_systems:
            for tech in system.technologies.all():
                tech_usage[tech] += 1
                # Track highest complexity achieved with each technology
                if tech not in tech_complexity or system.complexity > tech_complexity[tech]:
                    tech_complexity[tech] = system.complexity
        
        # Convert to list with mastery indicators
        mastery_breakdown = []
        for tech, usage_count in tech_usage.most_common():
            max_complexity = tech_complexity.get(tech, 1)
            
            # Determine mastery level
            if max_complexity >= 4 and usage_count >= 3:
                mastery = 'Advanced'
                color = 'coral'
            elif max_complexity >= 3 or usage_count >= 2:
                mastery = 'Intermediate'
                color = 'teal'
            else:
                mastery = 'Learning'
                color = 'yellow'
            
            mastery_breakdown.append({
                'technology': tech,
                'usage_count': usage_count,
                'max_complexity': max_complexity,
                'mastery_level': mastery,
                'mastery_color': color,
                'percentage': round((usage_count / featured_systems.count()) * 100, 1)
            })

        return mastery_breakdown[:8]  # Top 8 technologies
    
    def get_learning_insights(self, featured_systems):
        """Generate insights about the learning journey from featured projects."""
        insights = []
        
        # Most complex project
        most_complex = featured_systems.order_by('-complexity').first()
        if most_complex and most_complex.complexity >= 4:
            insights.append({
                'type': 'technical_achievement',
                'title': f'Advanced Implementation: {most_complex.title}',
                'description': f'Complexity Level {most_complex.complexity}/5 - Demonstrates sophisticated technical skills',
                'icon': 'trophy',
                'color': 'coral',
                'project_url': most_complex.get_absolute_url()
            })
        
        # Technology breadth
        unique_techs = featured_systems.values('technologies__name').distinct().count()
        if unique_techs >= 6:
            insights.append({
                'type': 'technology_breadth',
                'title': 'Full-Stack Proficiency',
                'description': f'Featured projects span {unique_techs} different technologies',
                'icon': 'code',
                'color': 'teal'
            })
        
        # Learning timeline
        project_span = self.get_development_span(featured_systems)
        if '>' in str(project_span) or 'month' in str(project_span):
            insights.append({
                'type': 'consistent_growth',
                'title': 'Consistent Development',
                'description': f'Continuous skill building over {project_span}',
                'icon': 'seedling',
                'color': 'mint'
            })
        
        return insights
    
    def get_available_sorts(self):
        """Get available sorting options for the portfolio."""
        return [
            {'key': 'complexity', 'label': 'Learning Progression (Simple → Complex)', 'icon': 'chart-line'},
            {'key': 'recent', 'label': 'Most Recent First', 'icon': 'clock'},
            {'key': 'completion', 'label': 'Completion Rate', 'icon': 'check-circle'},
            {'key': 'technology', 'label': 'By Technology Type', 'icon': 'layer-group'},
        ]
    
    def get_complexity_distribution(self, featured_systems):
        """Get complexity distribution for visualization."""
        distribution = {}
        for i in range(1, 6):
            count = featured_systems.filter(complexity=i).count()
            distribution[f'level_{i}'] = {
                'count': count,
                'percentage': round((count / featured_systems.count()) * 100, 1) if featured_systems.count() > 0 else 0,
                'label': {
                    1: 'Basic', 2: 'Intermediate', 3: 'Advanced', 
                    4: 'Complex', 5: 'Expert'
                }.get(i, 'Unknown')
            }
        
        return distribution


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

# ======================  GITHUB DATA VIEWS ==================


class GitHubIntegrationView(TemplateView):
    """View to display GitHub integration data w AURA theming."""
    template_name = 'projects/github_integration.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get GitHub service
        github_service = GitHubAPIService()

        try:
            # Local repository data (fast)
            local_repos = GitHubRepository.objects.select_related().prefetch_related('languages')

            # GitHub stats
            github_stats = self.get_github_stats(local_repos)

            # Get sync info
            sync_info = self.get_sync_info(local_repos)

            # Recent Activity (from API if needed)
            recent_activity = self.get_recent_activity(github_service)

            # NEW: Enhanced repositories with weekly tracking
            repos_with_tracking = GitHubRepository.objects.with_detailed_tracking()
            
            # NEW: Weekly tracking statistics
            weekly_stats = self.get_weekly_tracking_stats(repos_with_tracking)
            
            # NEW: Recent weekly activity across all tracked repos
            recent_weekly_activity = self.get_recent_weekly_activity(repos_with_tracking)
            
            # NEW: Monthly trends
            monthly_trends = self.get_monthly_trends(repos_with_tracking)

            context.update(
                {
                    "github_stats": github_stats,
                    "recent_repos": local_repos.filter(is_archived=False)[:6],
                    "top_languages": self.get_top_languages(local_repos),
                    "recent_activity": recent_activity,
                    "integration_status": "active",
                    "sync_info": sync_info,  # Add sync info
                    # NEW: Weekly tracking context
                    "repos_with_tracking": repos_with_tracking,
                    "weekly_stats": weekly_stats,
                    "recent_weekly_activity": recent_weekly_activity,
                    "monthly_trends": monthly_trends,
                    "show_weekly_panels": repos_with_tracking.count() > 0,
                    "sync_url": True,  # Flag for JavaScript initialization
                }
            )
        except GitHubAPIError as e:
            context.update({
                'integration_status': 'error',
                'error_message': str(e),
                'github_stats': {},
                'sync_info': self.get_sync_info([]),  # Empty sync info for error state
                'show_weekly_panels': False,
                'repos_with_tracking': GitHubRepository.objects.none(),
            })
        return context
    
    def get_weekly_tracking_stats(self, repos_with_tracking):
        """Get overview stats for weekly tracking."""
        
        if not repos_with_tracking.exists():
            return None
        
        # Get recent weekly data (last 4 weeks)
        recent_weeks = GitHubCommitWeek.objects.filter(
            repository__in=repos_with_tracking
        ).order_by('-year', '-week')[:4]
        
        if not recent_weeks:
            return None
        
        # Calculate stats
        total_recent_commits = sum(week.commit_count for week in recent_weeks)
        avg_commits_per_week = total_recent_commits / 4 if recent_weeks else 0
        
        # Most active repo this month
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        most_active_repo = GitHubCommitWeek.objects.filter(
            repository__in=repos_with_tracking,
            year=current_year,
            month=current_month
        ).values('repository__name').annotate(
            total_commits=Sum('commit_count')
        ).order_by('-total_commits').first()
        
        return {
            'total_tracked_repos': repos_with_tracking.count(),
            'total_recent_commits': total_recent_commits,
            'avg_commits_per_week': round(avg_commits_per_week, 1),
            'most_active_repo': most_active_repo,
            'tracking_active': True
        }

    def get_recent_weekly_activity(self, repos_with_tracking):
        """Get recent weekly activity for timeline."""
        
        recent_weeks = GitHubCommitWeek.objects.filter(
            repository__in=repos_with_tracking
        ).select_related('repository').order_by('-year', '-week')[:12]
        
        # Group by week for aggregated view
        weekly_totals = defaultdict(lambda: {'commit_count': 0, 'repos_active': 0, 'week_info': None})
        
        for week in recent_weeks:
            week_key = f"{week.year}-W{week.week:02d}"
            weekly_totals[week_key]['commit_count'] += week.commit_count
            if week.commit_count > 0:
                weekly_totals[week_key]['repos_active'] += 1
            if not weekly_totals[week_key]['week_info']:
                weekly_totals[week_key]['week_info'] = week
        
        return [
            {
                'week_label': data['week_info'].get_week_label(),
                'week_start': data['week_info'].week_start_date,
                'total_commits': data['commit_count'],
                'repos_active': data['repos_active'],
                'week_info': data['week_info']
            }
            for data in weekly_totals.values()
            if data['week_info']
        ][:8]  # Last 8 weeks

    def get_monthly_trends(self, repos_with_tracking):
        """Get monthly trends for visualization."""
        
        monthly_data = GitHubCommitWeek.objects.filter(
            repository__in=repos_with_tracking
        ).values('year', 'month', 'month_name').annotate(
            total_commits=Sum('commit_count'),
            repos_count=Count('repository', distinct=True)
        ).order_by('-year', '-month')[:6]
        
        return list(monthly_data)
    
    def get_github_stats(self, repositories):
        """Calculate GitHub statistics from local data."""
        total_repos = repositories.count()
        public_repos = repositories.filter(is_private=False).count()

        # Aggregate statistics
        stats = repositories.aggregate(
            total_stars=Sum('stars_count'),
            total_forks=Sum('forks_count'),
            total_size=Sum('size')
        )

        # Active repos (updated in last 6 months)
        six_months_ago = timezone.now() - timedelta(days=180)
        active_repos = repositories.filter(github_updated_at__gte=six_months_ago).count()

        return {
            'total_repositories': total_repos,
            'public_repositories': public_repos,
            'private_repositories': total_repos - public_repos,
            'total_stars': stats['total_stars'] or 0,
            'total_forks': stats['total_forks'] or 0,
            'total_size_mb': round((stats['total_size'] or 0) / 1024, 2),
            'active_repositories': active_repos,
            'activity_percentage': round((active_repos / total_repos * 100), 1) if total_repos > 0 else 0,
        }
    
    def get_top_languages(self, repositories):
        """Get top programming langs across all repos."""
        lang_stats = GitHubLanguage.objects.filter(
            repository__in=repositories
        ).values('language').annotate(
            total_bytes=Sum('bytes_count'),
            repo_count=Count('repository', distinct=True)
        ).order_by('-total_bytes')[:10]

        return lang_stats
    
    def get_sync_info(self, repositories):
        """Get synchronization info for display."""
        if not repositories:
            return {
                'last_sync': None,
                'last_sync_display': 'Never',
                'next_sync_hours': 24,
                'next_sync_display': 'In 24 hours',
                'total_repos_synced': 0,
            }
        
        # Get the most recently synced repo
        if hasattr(repositories, 'order_by'):
            # Queryset
            most_recent = repositories.order_by('-last_synced').first()
        else:
            # List
            most_recent = max(repositories, key=lambda r: r.last_synced) if repositories else None
        
        if not most_recent or not most_recent.last_synced:
            return {
                "last_sync": None,
                "last_sync_display": "Never",
                "next_sync_hours": 24,
                "next_sync_display": "In 24 hours",
                "total_repos_synced": 0,
            }
        
        last_sync = most_recent.last_synced

        # Calculate next sync time (1hr from last sync)
        next_sync = last_sync + timedelta(hours=1)
        now = timezone.now()

        if next_sync <= now:
            next_sync_display = 'Available Now'
            hours_until_next = 0
        else:
            time_until_next = next_sync - now
            hours_until_next = time_until_next.total_seconds() / 3600

            if hours_until_next < 1:
                minutes = int(time_until_next.total_seconds() / 60)
                next_sync_display = f'In {minutes} minutes'
            else:
                next_sync_display = f'In {hours_until_next:.1f} hours'
        
        # Format last sync time
        time_since_sync = now - last_sync
        if time_since_sync.total_seconds() < 60:
            last_sync_display = 'Just now'
        elif time_since_sync.total_seconds() < 3600:
            minutes_ago = int(time_since_sync.total_seconds() / 60)
            last_sync_display = f'{minutes_ago} minutes ago'
        elif time_since_sync.days == 0:
            hours_ago = int(time_since_sync.total_seconds() / 3600)
            last_sync_display = f'{hours_ago} hours ago'
        elif time_since_sync.days == 1:
            last_sync_display = '1 day ago'
        else:
            last_sync_display = f'{time_since_sync.days} days ago'
        
        return {
            'last_sync': last_sync,
            'last_sync_display': last_sync_display,
            'next_sync_hours': hours_until_next,
            'next_sync_display': next_sync_display,
            'total_repos_synced': len(repositories) if hasattr(repositories, '__len__') else repositories.count(),
        }
    
    def get_recent_activity(self, github_service):
        """Get recent activity from GitHub API (cached)."""
        try:
            # This will be cached by service
            repos = github_service.get_repositories(sort='updated', per_page=5)
            return repos
        except GitHubAPIError:
            # Fallback to local data
            return GitHubRepository.objects.order_by('-github_updated_at')[:5]

# =================================
# DJANGO GITHUB SYNC VIEW FOR AJAX
# =================================


@method_decorator(csrf_exempt, name='dispatch')
class GitHubSyncView(LoginRequiredMixin, View):
    """AJAX endpoint for GitHub data sync"""

    def post(self, request, *args, **kwargs):
        """Handle GitHub sync requests."""
        try:
            data = json.loads(request.body)
            force = data.get('force', False)

            # Capture management command output
            out = StringIO()

            # Run sync command
            call_command(
                'sync_github_data',
                stdout=out,
                force=force
            )

            output = out.getvalue()

            # Get updated sync info
            repos = GitHubRepository.objects.all()

            # Calculate updated stats
            sync_info = self.get_sync_info(repos)
            stats = self.get_updated_stats(repos)

            return JsonResponse({
                'success': True,
                'message': 'GitHub data synchronized successfully',
                'output': output,
                'sync_info': sync_info,
                'stats': stats
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
            }, status=500)
        
    def get_sync_info(self, repositories):
        """Get sync info for AJAX response."""
        if not repositories.exists():
            return {
                'last_sync_display': 'Never',
                'next_sync_display': 'In 24 hours',
                'total_repos_synced': 0,
            }
        
        most_recent = repositories.order_by('-last_synced').first()

        if not most_recent or not most_recent.last_synced:
            return {
                'last_sync_display': 'Never',
                'next_sync_display': 'In 24 hours',
                'total_repos_synced': repositories.count(),
            }
        
        last_sync = most_recent.last_synced
        next_sync = last_sync + timedelta(hours=1)
        now = timezone.now()

        # Calculate displays
        if next_sync <= now:
            next_sync_display = 'Available Now'
        else:
            time_until_next = next_sync - now
            hours_until_next = time_until_next.total_seconds() / 3600

            if hours_until_next < 1:
                minutes = int(time_until_next.total_seconds() / 60)
                next_sync_display = f'In {minutes} minutes'
            else:
                next_sync_display = f'In {hours_until_next:.1f} hours'
        
        time_since_sync = now - last_sync
        if time_since_sync.total_seconds() < 60:
            last_sync_display = 'Just now'
        elif time_since_sync.total_seconds() < 3600:
            minutes_ago = int(time_since_sync.total_seconds() / 60)
            last_sync_display = f'{minutes_ago} minutes ago'
        else:
            hours_ago = int(time_since_sync.total_seconds() / 3600)
            last_sync_display = f'{hours_ago} hours ago'
        
        return {
            'last_sync_display': last_sync_display,
            'next_sync_display': next_sync_display,
            'total_repos_synced': repositories.count(),
        }
    
    def get_updated_stats(self, repositories):
        """Get updated stats for AJAX response."""
        total_repos = repositories.count()

        if total_repos == 0:
            return {
                'total_repositories': 0,
                'total_stars': 0,
                'total_forks': 0,
                'active_repositories': 0
            }
        
        # Aggregate statistics
        stats = repositories.aggregate(
            total_stars=Sum('stars_count'),
            total_forks=Sum('forks_count')
        )

        # Active repos (updated in last 6 mo)
        six_months_ago = timezone.now() - timedelta(days=180)
        active_repos = repositories.filter(github_updated_at__gte=six_months_ago).count()

        return {
            'total_repositories': total_repos,
            'total_stars': stats['total_stars'] or 0,
            'total_forks': stats['total_forks'] or 0,
            'active_repositories': active_repos,
        }
    
    def get(self, request, *args, **kwargs):
        """Check for updates without syncing."""
        check_only = request.GET.get('check_only', False)

        if check_only:
            # Quick check logic here
            # Compare last sync time w GitHub API rate limit reset
            has_updates = self.check_for_updates()

            return JsonResponse({
                'has_updates': has_updates
            })
        
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    def check_for_updates(self):
        """Check if there are potential updates available."""
        # Simple check based on last sync time
        last_repo = GitHubRepository.objects.order_by('-last_synced').first()
        if not last_repo:
            return True
        
        # If last sync was more than 1hr ago, suggest update
        return last_repo.last_synced < timezone.now() - timedelta(hours=1)


# ============ GITHUB TEST VIEW ====================
class GitHubIntegrationTestView(TemplateView):
    """Test view for GitHub integration functionality."""

    template_name = "projects/github_test.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get some test repositories
        all_repos = GitHubRepository.objects.all()[:10]
        repos_with_tracking = GitHubRepository.objects.with_detailed_tracking()

        context.update(
            {
                "test_repos": all_repos[:3],  # First 3 for basic testing
                "all_repos": all_repos,
                "repos_with_tracking": repos_with_tracking,
            }
        )

        return context
