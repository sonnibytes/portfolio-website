"""
v2.0 w AURA Admin Context Processor
Provides navigation statistics and counts for the admin interface
"""

from django.db.models import Count, Avg, Sum
from django.utils import timezone
from .models import SocialLink


# New admin navigation context
def admin_navigation_context(request):
    """
    Provides navigation statistics for the admin sidebar.
    Only processes for admin URLs to avoid unnecessary queries on public pages.
    """

    # Only run for admin URLs
    if not request.path.startswith('/aura-admin/'):
        return {}
    
    try:
        # Import models to avoid circular imports
        from core.models import Skill, Education, Experience, Contact, SocialLink, PortfolioAnalytics
        from projects.models import SystemModule, Technology, SystemType, ArchitectureComponent, ArchitectureConnection
        from blog.models import Post, Category, Series, Tag

        # Core App Stats
        skill_stats = {
            'total_skills': Skill.objects.count(),
            'featured_skills': Skill.objects.filter(is_featured=True).count(),
            'currently_learning': Skill.objects.filter(is_currently_learning=True).count(),
            'certified_skills': Skill.objects.filter(is_certified=True).count(),
        }

        education_stats = {
            'total_education': Education.objects.count(),
            'current_education': Education.objects.filter(is_current=True).count(),
            'completed_courses': Education.objects.filter(
                learning_type__in=['online_course', 'certification'],
                end_date__isnull=False,
            ).count(),
        }

        experience_stats = {
            'total_experience': Experience.objects.count(),
            'current_positions': Experience.objects.filter(is_current=True).count(),
            'total_companies': Experience.objects.values('company').distinct().count(),
        }

        contact_stats = {
            'total_contacts': Contact.objects.count(),
            'unread_contacts': Contact.objects.filter(is_read=False).count(),
            'high_priority_contacts': Contact.objects.filter(priority='high').count(),
            'top_priority_contacts': Contact.objects.filter(priority__in=['high', 'urgent']).count(),
            'pending_responses': Contact.objects.filter(
                is_read=True,
                response_sent=False
            ).count(),
        }

        social_stats = {
            'total_social_links': SocialLink.objects.count(),
            'professional_links': SocialLink.objects.filter(category='professional').count(),
            'community_links': SocialLink.objects.filter(category='community').count(),
            'chat_links': SocialLink.objects.filter(category='chat').count(),
        }

        # Projects App Stats
        system_stats = {
            'total_systems': SystemModule.objects.count(),
            'active_systems': SystemModule.objects.filter(status__in=['deployed', 'published']).count(),
            'development_systems': SystemModule.objects.filter(status__in=['in_development', 'testing']).count(),

            # Added context for experimental architecture dashboard rework
            'total_system_types': SystemType.objects.count(),
            # Adding as dupe for now, can remove technology_stats below if I like the flow
            'total_technologies': Technology.objects.count(),
        }

        system_type_stats = {
            
        }

        ## ADDED Architecture context
        architecture_stats = {
            'total_components': ArchitectureComponent.objects.count(),
            'total_connections': ArchitectureConnection.objects.count(),
            'systems_with_architecture': SystemModule.objects.filter(
                architecture_components__isnull=False
            ).distinct().count(),
            'core_components': ArchitectureComponent.objects.filter(is_core=True).count(),
        }

        technology_stats = {
            'total_technologies': Technology.objects.count(),
            'language_count': Technology.objects.filter(category='language').count(),
            'framework_count': Technology.objects.filter(category='framework').count(),
            'database_count': Technology.objects.filter(category='database').count(),
            'cloud_count': Technology.objects.filter(category='cloud').count(),
            'tool_count': Technology.objects.filter(category='tool').count(),
            'os_count': Technology.objects.filter(category='os').count(),
            'ai_count': Technology.objects.filter(category='ai').count(),
        }

        # DataLogs Stats
        datalogs_stats = {
            'total_posts': Post.objects.count(),
            'published_posts': Post.objects.filter(status='published').count(),
            'draft_posts': Post.objects.filter(status='draft').count(),
            'total_categories': Category.objects.count(),
            'total_series': Series.objects.count(),
            'total_tags': Tag.objects.count(),
        }


        # Integration Stats
        from core.models import EducationSkillDevelopment, SkillTechnologyRelation
        integration_stats = {
            'education_skill_connection': EducationSkillDevelopment.objects.count(),
            'skill_tech_relations': SkillTechnologyRelation.objects.count(),
            'total_connections': (
                EducationSkillDevelopment.objects.count() + SkillTechnologyRelation.objects.count()
            ),
        }

        return {
            'skill_stats': skill_stats,
            'education_stats': education_stats,
            'experience_stats': experience_stats,
            'contact_stats': contact_stats,
            'social_stats': social_stats,
            'system_stats': system_stats,
            'architecture_stats': architecture_stats,
            'technology_stats': technology_stats,
            'datalog_stats': datalogs_stats,
            'integration_stats': integration_stats,
        }
    
    except Exception as e:
        # Gracefully handle any import or db errors
        # Return empty stats if there's an issue
        return {
            'skill_stats': {'currently_learning': 0},
            'education_stats': {'current_education': 0},
            'experience_stats': {},
            'contact_stats': {'unread_contacts': 0},
            'social_stats': {'total_social_links': 0},
            'system_stats': {'total_systems': 0},
            'technology_stats': {'total_technologies': 0},
            'blog_stats': {'draft_posts': 0},
            'integration_stats': {'total_connections': 0},
        }


def global_context(request):
    """Add global context variables to all templates."""
    return {
        'social_links': SocialLink.objects.all().order_by('display_order'),
    }


def admin_context(request):
    """Add global admin context to all templates."""

    context = {}

    # Check if user is in admin area
    if request.path.startswith("/aura-admin/"):
        context["in_admin"] = True

        # Add admin navigation data
        if request.user.is_authenticated and (
            request.user.is_staff or request.user.is_superuser
        ):
            # Import here to avoid circular imports
            try:
                from blog.models import Post, Category
                from projects.models import SystemModule, Technology

                context.update(
                    {
                        "admin_stats": {
                            "total_posts": Post.objects.count(),
                            "total_systems": SystemModule.objects.count(),
                            "total_categories": Category.objects.count(),
                            "total_technologies": Technology.objects.count(),
                        },
                        "admin_quick_links": [
                            {
                                "name": "DataLogs",
                                "url": "/aura-admin/blog/",
                                "icon": "fas fa-database",
                                "color": "lavender",
                            },
                            {
                                "name": "Systems",
                                "url": "/aura-admin/projects/",
                                "icon": "fas fa-microchip",
                                "color": "cyan",
                            },
                        ],
                    }
                )
            except ImportError:
                # If models don't exist yet, provide empty stats
                context.update(
                    {
                        "admin_stats": {
                            "total_posts": 0,
                            "total_systems": 0,
                            "total_categories": 0,
                            "total_technologies": 0,
                        },
                        "admin_quick_links": [],
                    }
                )

    return context
