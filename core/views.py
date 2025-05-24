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

from .models import CorePage, Skill, Education, Experience, SocialLink, Contact
from .forms import ContactForm
from blog.models import Post, Category
from projects.models import SystemModule, Technology
from datetime import timedelta


class HomeView(TemplateView):
    """AURA Home/Dashboard View with comprehensive system metrics."""
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # AURA System Metrics
        context['total_systems'] = SystemModule.objects.filter(
            status__in=['deployed', 'published']
        ).count() or 12

        context['total_logs'] = Post.objects.filter(
            status='published'
        ).count() or 24

        context['technologies_count'] = Technology.objects.count() or 15

        # Featured Systems (limit 3 for homepage)
        context['featured_projects'] = SystemModule.objects.filter(
            featured=True,
            status__in=['deployed', 'published']
        ).select_related('system_type').prefetch_related(
            'technologies').order_by('-created')[:3]

        # Latest DataLogs (limit 3 for homepage)
        context['latest_posts'] = Post.objects.filter(
            status='published'
        ).select_related('category').order_by('-published_date')[:3]

        # Quick Stats for Dashboard Cards
        context['deployed_systems'] = SystemModule.objects.filter(
            status__in=['deployed', 'published']
        ).count() or 8

        context['in_development'] = SystemModule.objects.filter(
            status='in_development'
        ).count() or 3

        context['ml_projects'] = SystemModule.objects.filter(
            Q(title__icontains='ML') |
            Q(title__icontains='Machine Learning') |
            Q(description__icontains='machine learning') |
            Q(description__icontains='neural') |
            Q(technologies__name__icontains='TensorFlow') |
            Q(technologies__name__icontains='PyTorch')
        ).distinct().count() or 5

        context['recent_logs'] = Post.objects.filter(
            status='published',
            published_date__gte=timezone.now() - timedelta(days=30)
        ).count() or 12

        # System Status Metrics for HUD displays
        context['system_metrics'] = {
            'uptime': '99.7%',
            'response_time': '142ms',
            'security_level': 'AES-256',
            'active_connections': '1,247',
            'total_deployments': SystemModule.objects.filter(
                status='deployed').count(),
            'avg_completion': SystemModule.objects.aggregate(
                avg=Avg('completion_percent')
            )['avg'] or 85.0,
        }

        # Categories for navigation
        context['categories'] = Category.objects.all()[:5]

        # Additional metrics for status display
        context['systems_tested'] = SystemModule.objects.filter(
            status='testing'
        ).count() or 2

        # TODO: Get from GitHub API
        context['lines_of_code'] = 50000
        # TODO: Get from GitHub API
        context['commits_this_month'] = 127

        return context


class DeveloperProfileView(TemplateView):
    """
    Comprehensive AURA Developer Profile with integrated resume functionality.
    Combines profile display with downloadable resume generation.
    """
    template_name = 'core/developer-profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Skills grouped by category
        skill_categories = {}
        for category, label in Skill.CATEGORY_CHOICES:
            skills = Skill.objects.filter(
                category=category).order_by("display_order")
            if skills.exists():
                skill_categories[category] = {"label": label, "skills": skills}
        context["skill_categories"] = skill_categories

        # Education background
        context["education"] = Education.objects.all()

        # Professional experience
        context["experiences"] = Experience.objects.all()

        # Social/Network links
        context["social_links"] = SocialLink.objects.all()

        # Portfolio & System Metrics
        context["portfolio_metrics"] = {
            "total_systems": SystemModule.objects.filter(
                status__in=["deployed", "published"]
            ).count()
            or 12,
            "systems_completed": SystemModule.objects.filter(
                status="deployed").count()
            or 8,
            "systems_in_progress": SystemModule.objects.filter(
                status="in_development"
            ).count()
            or 3,
            "total_logs_count": Post.objects.filter(
                status="published").count() or 24,
            "technologies_mastered": Technology.objects.count() or 15,
            "languages_used": Technology.objects.filter(
                category="language").count()
            or 8,
            "coding_years": 3,
            # TODO: Get from GitHub API
            "github_repos": 25,
            # TODO: Can get from GitHub API
            "lines_of_code": 50000,
            # TODO: Get from GitHub API
            "contributions_this_year": 284,
        }

        # Recent Activity for timeline
        context['recent_systems'] = SystemModule.objects.filter(
            status__in=['deployed', 'published']
        ).order_by('-created')[:3]

        context['recent_posts'] = Post.objects.filter(
            status='published'
        ).order_by('-published_date')[:3]

        # Tech Breakdown
        context['tech_by_category'] = {}
        for category, label in Technology.CATEGORY_CHOICES:
            techs = Technology.objects.filter(category=category)
            if techs.exists():
                context['tech_by_category'][category] = {
                    'label': label,
                    'technologies': techs[:8]
                }

        return context


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
            "last_updated": self.object.updated,
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
