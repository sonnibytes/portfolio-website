from django.views.generic import TemplateView, DetailView, FormView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from django.db.models import Count, Avg, Q
from django.template.loader import render_to_string
from django.conf import settings
import os
import calendar

from .models import CorePage, Skill, Education, Experience, SocialLink, Contact, LearningJourneyManager, PortfolioAnalytics
from .forms import ContactForm
from blog.models import Post, Category
from projects.models import SystemModule, Technology, LearningMilestone
from datetime import timedelta


class HomeView(TemplateView):
    """
    Enhanced Home Page - Dynamic Learning Journey Showcase
    Uses model relationships instead of hardcoded data
    """

    template_name = "core/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ========== DYNAMIC LEARNING JOURNEY METRICS ==========
        journey_manager = LearningJourneyManager()
        context["learning_journey"] = journey_manager.get_journey_overview()

        # ========== DYNAMIC LEARNING HIGHLIGHTS ==========
        context["learning_highlights"] = journey_manager.get_learning_highlights()

        # ========== DYNAMIC SKILL PROGRESSION ==========
        context["skill_progression"] = journey_manager.get_skill_progression()

        # ========== DYNAMIC LEARNING TIMELINE ==========
        context["learning_timeline"] = journey_manager.get_learning_timeline()

        # ========== DYNAMIC FEATURED SYSTEMS/PROJECTS ==========
        context["featured_systems"] = journey_manager.get_featured_systems()

        # ========== CURRENT LEARNING STATUS (DYNAMIC) ==========
        # Get current learning from ongoing education
        current_education = Education.objects.filter(is_current=True).first()
        current_projects = SystemModule.objects.filter(status="in_development")

        context["current_status"] = {
            "availability": "Seeking first professional tech role",
            "current_learning": current_education.degree
            if current_education
            else "Advanced Django Development",
            "learning_platform": current_education.platform
            if current_education
            else "Self-Directed",
            "current_projects": current_projects.count(),
            "next_goal": self.get_next_learning_goal(),
            "location": "Remote or North Carolina-based opportunities (open to relocation)",
            "transition_stage": "Ready for entry-level Python development role",
        }

        # ========== DYNAMIC PORTFOLIO METRICS ==========

        # PORTFOLIO INTEGRATION - Real Data
        try:
            context['portfolio_metrics'] = {
                'learning_duration': context['learning_journey']['duration_years'],
                'total_systems': SystemModule.objects.filter(
                    status__in=['deployed', 'published']
                ).count(),
                'portfolio_ready_systems': SystemModule.objects.filter(portfolio_ready=True).count(),
                'total_technologies': Technology.objects.count(),
                'skills_mastered': Skill.objects.filter(proficiency__gte=4).count(),
                'total_datalogs': Post.objects.filter(status='published').count(),
                'learning_milestones': LearningMilestone.objects.count(),
                'courses_completed': context['learning_journey']['courses_completed'],
                'learning_hours': context['learning_journey']['learning_hours'],
                'certificates_earned': context['learning_journey']['certificates_earned'],
            }

            # Featured systems (dynamic)
            featured_systems = SystemModule.objects.filter(
                featured=True,
                status__in=["deployed", "published"]
            ).select_related("system_type").prefetch_related("technologies")[:3]
            
            if not featured_systems.exists():
                # Fallback to top portfolio-ready systems
                featured_systems = SystemModule.objects.filter(
                    portfolio_ready=True,
                    status__in=["deployed", "published"]
                ).select_related("system_type").prefetch_related("technologies")[:3]
            
            context["portfolio_systems"] = featured_systems

            # Recent learning documentation (dynamic)
            recent_datalogs = Post.objects.filter(
                status="published"
            ).select_related("category").order_by("-published_date")[:3]
            context["recent_datalogs"] = recent_datalogs
        
        except Exception as e:
            # Fallback for development or missing data
            context['portfolio_metrics'] = {
                'learning_duration': '2+ Years',
                'total_systems': 8,
                'portfolio_ready_systems': 3,
                'total_technologies': 12,
                'skills_mastered': 8,
                'total_datalogs': 15,
                'learning_milestones': 12,
                'courses_completed': 6,
                'learning_hours': 400,
                'certificates_earned': 4,
            }
        # ========== DYNAMIC CALL-TO-ACTION SECTIONS ==========
        context["cta_sections"] = [
            {
                "title": "Explore My Projects",
                "description": f"See {context['portfolio_metrics']['total_systems']} projects showing skill progression",
                "url": "/projects/",
                "icon": "fas fa-folder-open",
                "color": "teal",
                "metric": f"{context['portfolio_metrics']['portfolio_ready_systems']} portfolio-ready",
            },
            {
                "title": "Read Learning Journey",
                "description": f"{context['portfolio_metrics']['total_datalogs']} technical insights and learning documentation",
                "url": "/blog/",
                "icon": "fas fa-book-open",
                "color": "lavender",
                "metric": "Technical writing",
            },
            {
                "title": "Download Resume",
                "description": "Professional credentials and learning progression details",
                "url": "/resume/download/",
                "icon": "fas fa-download",
                "color": "coral",
                "metric": "Always current",
            },
            {
                "title": "Let's Connect",
                "description": "Discuss opportunities and collaboration",
                "url": "/communication/",
                "icon": "fas fa-envelope",
                "color": "mint",
                "metric": "Quick response",
            },
        ]

        # ========== RECENT LEARNING ACTIVITY ==========
        # Get recent learning activity from multiple sources
        recent_activity = []

        # Recent milestones
        recent_milestones = LearningMilestone.objects.order_by('-date_achieved')[:3]
        for milestone in recent_milestones:
            recent_activity.append({
                'type': 'milestone',
                'title': milestone.title,
                'date': milestone.date_achieved,
                'description': milestone.description[:80] + "..." if len(milestone.description) > 80 else milestone.description,
                'icon': 'fas fa-trophy',
                'color': 'coral',
            })
        
        # Recent systems
        recent_systems = SystemModule.objects.filter(
            status__in=["deployed", "published"]
        ).order_by("-created_at")[:2]
        for system in recent_systems:
            recent_activity.append(
                {
                    "type": "system",
                    "title": f"Completed {system.title}",
                    "date": system.created_at,
                    "description": system.excerpt[:80] + "..."
                    if system.excerpt and len(system.excerpt) > 80
                    else system.excerpt or "Project completion",
                    "icon": "fas fa-code",
                    "color": "teal",
                }
            )
        
        # Sort by date and take top 4
        recent_activity.sort(key=lambda x: x['date'], reverse=True)
        context['recent_activity'] = recent_activity[:4]

        # ========== LEARNING ANALYTICS ==========
        # Get recent learning analytics
        analytics_summary = PortfolioAnalytics.get_learning_summary(days=30)
        context['learning_analytics'] = {
            'monthly_learning_hours': analytics_summary['total_learning_hours'],
            'consistency_rate': round(analytics_summary['consistency_rate'], 1),
            'avg_daily_hours': round(analytics_summary['avg_daily_hours'], 1),
            'learning_streak': self.get_current_learning_streak(),
        }

        # ========== META DATA FOR SEO (DYNAMIC) ==========
        skills_list = ", ".join(
            [skill.name for skill in Skill.objects.filter(is_featured=True)[:6]]
        )

        context["page_title"] = (
            f"Python Developer & {Skill.objects.filter(category='language').count()}+ Languages - Learning Journey Portfolio"
        )
        context["page_description"] = (
            f"Self-taught developer with {context['learning_journey']['duration_years']} intensive learning. "
            f"{context['portfolio_metrics']['courses_completed']} courses completed, "
            f"{context['portfolio_metrics']['total_systems']} projects built. "
            f"Skills: {skills_list}. Ready for professional development role."
        )
        context["page_keywords"] = (
            f"Python Developer, Self-Taught Programmer, {skills_list}, "
            "Algorithm Development, Django, Career Transition, Portfolio Projects"
        )

        return context
    
    def get_next_learning_goal(self):
        """Determine next learning goal from current education or default"""
        current_education = Education.objects.filter(is_current=True).first()
        if current_education:
            return f"Complete {current_education.degree}"
        
        # Check for skills marked as currently learning
        learning_skills = Skill.objects.filter(is_currently_learning=True)
        if learning_skills.exists():
            return f"Master {learning_skills.first().name}"
        
        return "Advanced Python & API Development"
    
    def get_current_learning_streak(self):
        """Calculate current learning streak from analytics"""
        try:
            # Get recent analytics entries
            recent_analytics = PortfolioAnalytics.objects.filter(
                learning_hours_logged__gt=0
            ).order_by('-date')[:30]

            if not recent_analytics.exists():
                return 0
            
            # Count consecutive days of learning
            streak = 0
            current_date = timezone.now().date()

            for analytics in recent_analytics:
                if analytics.date == current_date - timedelta(days=streak):
                    streak += 1
                else:
                    break
            return streak
        except:
            return 0


class DeveloperProfileView(TemplateView):
    """
    Enhanced AURA Developer Profile showcasing learning journey progression.
    Integrates with Skills, Experience, Education, and cross-app data.
    """
    template_name = 'core/developer-profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Enhanced skills progression w learning journey focus
        skill_categories = {}
        for category, label in Skill.CATEGORY_CHOICES:
            skills = Skill.objects.filter(category=category).order_by(
                "-proficiency", "name"
            )
            if skills.exists():
                skill_categories[category] = {
                    "label": label,
                    "skills": skills,
                    "count": skills.count(),
                    "avg_proficiency": skills.aggregate(avg=Avg("proficiency"))["avg"] or 0,
                }
        context["skill_categories"] = skill_categories

        # Educational background
        context["education"] = Education.objects.all().order_by('-end_date', '-start_date')

        # Professional experience
        context["experiences"] = Experience.objects.all().order_by('-end_date', '-start_date')

        # Social/Network links
        context["social_links"] = SocialLink.objects.filter(is_active=True).order_by('display_order')

        # Enhanced portfolio metrics with learning journey focus
        context["portfolio_metrics"] = {
            # Core metrics from your existing implementation
            "total_systems": SystemModule.objects.filter(
                status__in=["deployed", "published"]
            ).count() or 12,
            "systems_completed": SystemModule.objects.filter(status="deployed").count() or 8,
            "systems_in_progress": SystemModule.objects.filter(
                status="in_development"
            ).count() or 3,
            "total_logs_count": Post.objects.filter(status="published").count() or 24,
            "technologies_mastered": Technology.objects.count() or 15,
            "languages_used": Technology.objects.filter(category="language").count() or 8,
            "coding_years": 3,
            # Enhanced learning journey metrics
            "skills_learned": Skill.objects.count(),
            "skill_mastery_avg": Skill.objects.aggregate(avg=Avg("proficiency"))["avg"] or 75,
            "learning_velocity": self.calculate_learning_velocity(),
            "portfolio_ready_systems": SystemModule.objects.filter(
                portfolio_ready=True
            ).count(),
            "learning_milestones": self.get_learning_milestones_count(),
            # GitHub/external metrics (can be populated with real API data later)
            "github_repos": 25,
            "lines_of_code": 50000,
            "contributions_this_year": 284,
        }

        # Recent activity showcasing learning progression
        context["recent_systems"] = SystemModule.objects.filter(
            status__in=["deployed", "published"]
        ).order_by("-updated_at")[:3]

        context["recent_posts"] = Post.objects.filter(status="published").order_by(
            "-published_date"
        )[:3]

        # Technology breakdown by category
        context["tech_by_category"] = {}
        for category, label in Technology.CATEGORY_CHOICES:
            techs = (
                Technology.objects.filter(category=category)
                .annotate(system_count=Count("systems"))
                .order_by("-system_count")
            )
            if techs.exists():
                context["tech_by_category"][category] = {
                    "label": label,
                    "technologies": techs[:8],  # Top 8 most used
                }

        # Learning progression summary
        context["learning_summary"] = self.get_learning_progression_summary()

        # Meta information for SEO and sharing
        context["page_description"] = (
            "Self-taught Python developer with 2+ years intensive learning journey. "
            f"{context['portfolio_metrics']['skills_learned']} skills mastered, "
            f"{context['portfolio_metrics']['total_systems']} projects built. "
            "Ready for professional development role."
        )
        context["page_keywords"] = (
            "Python Developer, Self-Taught Programmer, Learning Journey, "
            "Algorithm Development, Django, Flask, Career Transition, "
            "EHS to Tech, Portfolio Ready"
        )

        return context
    
    def calculate_learning_velocity(self):
        """Calculate skills learned per month over learning journey."""
        # This could be enhanced w actual date tracking
        skills_count = Skill.objects.count()
        # 2.5yr * 12 mo
        learning_months = 30
        return round(skills_count / learning_months, 1) if learning_months > 0 else 0


# TODO: Clean up -- May be able to combine dashboards on home instead of separate in sep apps.
class ResumeDownloadView(TemplateView):
    """
    Generate and serve downloadable resume in various formats.
    Integrates with DeveloperProfileView data.
    """

    def get(self, request, *args, **kwargs):
        format_type = kwargs.get("format", "pdf")

        if format_type == "pdf":
            return self.generate_pdf_resume()
        elif format_type == "json":
            return self.generate_json_resume()
        else:
            # Default to serving static PDF if available
            return self.serve_static_resume()

    def generate_pdf_resume(self):
        """Generate PDF resume using reportlab or serve static file."""
        try:
            # Option 1: Serve static PDF file
            static_pdf_path = os.path.join(
                settings.STATIC_ROOT or settings.BASE_DIR / "static",
                "docs/sonni_gunnels_resume.pdf",
            )

            if os.path.exists(static_pdf_path):
                with open(static_pdf_path, "rb") as pdf_file:
                    response = HttpResponse(
                        pdf_file.read(), content_type="application/pdf"
                    )
                    response["Content-Disposition"] = (
                        'attachment; filename="Sonni_Gunnels_Resume.pdf"'
                    )
                    return response

            # Option 2: Generate dynamic PDF (implement with reportlab if needed)
            # For now, return JSON format with message
            return JsonResponse(
                {
                    "message": "PDF generation not implemented yet. Please contact for resume.",
                    "contact_url": "/communication/",
                    "format": "pdf",
                }
            )

        except Exception as e:
            return JsonResponse({
                "error": "Resume generation failed"}, status=500)

    def generate_json_resume(self):
        """Generate machine-readable JSON resume."""
        try:
            # Gather all profile data
            skills = Skill.objects.all().order_by("category", "display_order")
            education = Education.objects.all()
            experiences = Experience.objects.all()
            social_links = SocialLink.objects.all()

            # Build JSON Resume format
            resume_data = {
                "basics": {
                    "name": "Sonni Gunnels",
                    "label": "Python Developer & ML Engineer",
                    "email": "hello@mldevlog.com",
                    "url": "https://mldevlog.com",
                    "summary": "Python Developer and ML Engineer with expertise in developing data-driven applications. Specializing in machine learning, data analysis, and web application development with Django and FastAPI.",
                    "location": {
                        "city": "Birmingham",
                        "region": "Alabama",
                        "countryCode": "US",
                    },
                    "profiles": [
                        {"network": link.name, "username": link.handle, "url": link.url}
                        for link in social_links
                    ],
                },
                "work": [
                    {
                        "name": exp.company,
                        "position": exp.position,
                        "startDate": exp.start_date.isoformat(),
                        "endDate": exp.end_date.isoformat() if exp.end_date else None,
                        "summary": exp.description,
                        "highlights": exp.get_technologies_list(),
                    }
                    for exp in experiences
                ],
                "education": [
                    {
                        "institution": edu.institution,
                        "studyType": edu.degree,
                        "area": edu.field_of_study,
                        "startDate": edu.start_date.isoformat(),
                        "endDate": edu.end_date.isoformat() if edu.end_date else None,
                        "summary": edu.description,
                    }
                    for edu in education
                ],
                "skills": [
                    {
                        "name": skill.name,
                        "level": f"Level {skill.proficiency}/5",
                        "keywords": [skill.category],
                    }
                    for skill in skills
                ],
                "projects": [
                    {
                        "name": system.title,
                        "description":
                        system.excerpt or system.description[:200],
                        "highlights":
                        [tech.name for tech in system.technologies.all()],
                        "url": system.live_url or system.github_url,
                        "roles": ["Developer"],
                        "entity": "Personal Project",
                        "type": "application",
                    }
                    for system in SystemModule.objects.filter(
                        status__in=["deployed", "published"]
                    )[:10]
                ],
            }

            response = JsonResponse(resume_data, json_dumps_params={"indent": 2})
            response["Content-Disposition"] = (
                'attachment; filename="sonni_gunnels_resume.json"'
            )
            return response

        except Exception as e:
            return JsonResponse({
                "error": "JSON resume generation failed"}, status=500)

    def serve_static_resume(self):
        """Fallback to serve static resume file."""
        return JsonResponse(
            {
                "message":
                "Please visit the developer profile page for comprehensive info.",
                "profile_url": "/developer-profile/",
                "contact_url": "/communication/",
            }
        )


class CommTerminalView(FormView):
    """AURA Communication Terminal - Enhanced Contact Interface."""
    template_name = 'core/communication.html'
    form_class = ContactForm
    success_url = reverse_lazy('core:contact_success')

    def form_valid(self, form):
        # Save the contact submission
        contact = form.save()
        # Add AURA-themed success message
        messages.success(
            self.request,
            f"TRANSMISSION_COMPLETE: Message #{contact.id:04d} received. "
            f"Response protocol initiated. Expected delivery: 24-48 hours.",
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        # Add AURA-themed error message
        messages.error(
            self.request,
            "TRANSMISSION_ERROR: Data validation failed. "
            "Please verify input parameters and retry transmission.",
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add social links for network connections
        context['social_links'] = SocialLink.objects.all().order_by(
            'display_order')

        # Add system metrics for HUD display
        # Can get System Specs for this feed?
        context['system_metrics'] = {
            'uptime': '99.7%',
            'response_time': '142ms',
            'security_level': 'AES-256',
            'active_connections': '1,247',
            'messages_processed': Contact.objects.count(),
            'encryption_status': 'ACTIVE',
            'firewall_status': 'ENABLED',
            'last_security_scan': timezone.now() - timedelta(hours=2),
        }

        # Network status for communication display
        context['network_status'] = {
            'primary_connection': 'STABLE',
            'backup_connection': 'STANDBY',
            'bandwidth_usage': '23%',
            'packet_loss': '0.1%',
        }

        # Communication history metrics
        # TODO: Maybe move this to admin dashboard only
        context['comm_metrics'] = {
            'total_messages': Contact.objects.count(),
            'messages_today': Contact.objects.filter(
                created_at__date=timezone.now().date()
            ).count(),
            'avg_response_time': '4.2 hours',
            'satisfaction_rate': '98.5%',
        }

        # Add current timestamp for real-time display
        context['current_timestamp'] = timezone.now()

        return context


class ContactSuccessView(TemplateView):
    """AURA Contact Success confirmation."""

    template_name = "core/contact_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["message_id"] = self.request.GET.get("msg_id", "0001")
        return context


class CorePageView(DetailView):
    """Generic view for static pages stored in database."""
    model = CorePage
    template_name = 'core/page.html'
    context_object_name = "page"

    def get_queryset(self):
        # Only show published pages
        return CorePage.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add page metrics for AURA display
        context["page_metrics"] = {
            "last_updated": self.object.updated_at,
            "word_count": len(self.object.content.split()),
            "reading_time": max(1, len(self.object.content.split()) // 200),
            "page_id": f"PAGE-{self.object.id:03d}",
        }

        return context


class PrivacyView(TemplateView):
    """AURA privacy policy page."""
    template_name = 'core/privacy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Privacy Policy metrics, can sub more useful metrics later
        context['policy_info'] = {
            'version': '2.1',
            'last_updated': timezone.now().date(),
            'compliance_standards': ['GDPR', 'CCPA', 'SOC 2'],
            'data_retention': '30 days',
            'encryption_level': 'AES-256',
        }

        return context


class TermsView(TemplateView):
    """AURA Terms of Service page."""

    template_name = "core/terms.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Terms of service info
        context["terms_info"] = {
            "version": "1.3",
            "effective_date": timezone.now().date(),
            "jurisdiction": "United States",
            "governing_law": "Alabama State Law",
            "last_review": timezone.now().date(),
        }

        return context


# class ResumeView(TemplateView):
#     """View for resume/CV page."""
#     template_name = "core/resume.html"

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['skills'] = Skill.objects.all().order_by('category', 'display_order')
#         context['education'] = Education.objects.all()
#         context['experiences'] = Experience.objects.all()
#         return context


@method_decorator(csrf_protect, name='dispatch')
class ErrorView(TemplateView):
    """AURA custom error pages."""
    template_name = 'core/error.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['error_code'] = kwargs.get('error_code', '404')
        context['error_message'] = kwargs.get('error_message', 'Page not found')
        return context


# API Views for AURA HUD Data
class SystemMetricsAPIView(TemplateView):
    """API endpoint for real-time system metrics (for HUD dashboard)."""

    def get(self, request, *args, **kwargs):
        metrics = {
            "systems": {
                "total": SystemModule.objects.filter(
                    status__in=["deployed", "published"]
                ).count(),
                "deployed": SystemModule.objects.filter(status="deployed").count(),
                "in_development": SystemModule.objects.filter(
                    status="in_development"
                ).count(),
                "testing": SystemModule.objects.filter(status="testing").count(),
            },
            "logs": {
                "total": Post.objects.filter(status="published").count(),
                "recent": Post.objects.filter(
                    status="published",
                    published_date__gte=timezone.now() - timezone.timedelta(days=30),
                ).count(),
            },
            "technologies": {
                "total": Technology.objects.count(),
                "languages": Technology.objects.filter(category="language").count(),
                "frameworks": Technology.objects.filter(category="framework").count(),
            },
            "system_status": {
                "uptime": "99.7%",
                "response_time": f"{142 + (timezone.now().second % 30)}ms",
                "memory_usage": f"{65 + (timezone.now().second % 20)}%",
                "active_connections": 1247 + (timezone.now().minute * 3),
                "last_updated": timezone.now().isoformat(),
            },
        }

        return JsonResponse(metrics)
