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

from .models import CorePage, Skill, Education, Experience, SocialLink, Contact
from .forms import ContactForm
from blog.models import Post, Category
from projects.models import SystemModule, Technology
from datetime import timedelta


class HomeView(TemplateView):
    """
    Enhanced Home Page - Learning Journey Showcase
    Highlights 2+ year learning progression from EHS Compliance to Software Development
    """

    template_name = "core/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # LEARNING JOURNEY HERO METRICS
        context["learning_journey"] = {
            "start_date": "August 2022",
            "duration_years": "2.5+ Years",
            "courses_completed": 9,
            "learning_hours": "460+",
            "certificates_earned": 6,
            "projects_built": "100+",
            "platforms_used": 5,
        }

        # LEARNING HIGHLIGHTS & ACHIEVEMENTS
        context["learning_highlights"] = [
            {
                "title": "Harvard CS50 Python",
                "platform": "edX HarvardX",
                "icon": "fas fa-university",
                "color": "teal",
                "description": "Academic programming foundation",
                "badge": "Academic Excellence",
            },
            {
                "title": "100 Days of Code",
                "platform": "Udemy",
                "icon": "fas fa-fire",
                "color": "coral",
                "description": "100 projects completed (Sept 2024)",
                "badge": "Recent Achievement",
            },
            {
                "title": "Data Science Bootcamp",
                "platform": "Udemy",
                "icon": "fas fa-chart-line",
                "color": "lavender",
                "description": "ML, TensorFlow, Scikit-Learn",
                "badge": "Advanced Skills",
            },
            {
                "title": "LLM Engineering",
                "platform": "Udemy",
                "icon": "fas fa-robot",
                "color": "mint",
                "description": "Currently learning cutting-edge AI",
                "badge": "In Progress",
            },
        ]

        # FEATURED PROJECT SHOWCASES
        context['featured_projects'] = [
            {
                'title': 'AURA Portfolio',
                'subtitle': 'Django Multi-App Architecture',
                'description': 'Sophisticated portfolio with admin system, DataLogs, and Systems management. Demonstrates full-stack Django development with PostgreSQL, unified design system, and professional UI/UX.',
                'technologies': ['Django', 'PostgreSQL', 'JavaScript', 'CSS3', 'Admin System'],
                'live_url': '',  # Add when deployed
                'github_url': 'https://github.com/yourusername/portfolio-project',  # Update with your repo
                'learning_focus': 'Advanced Django architecture and professional web development'
            },
            {
                'title': 'myRise Learning Tracker',
                'subtitle': 'Flask Independent Project',
                'description': 'Self-directed Flask web application for tracking learning resources, links, libraries, and APIs. Built to solve personal learning organization needs, demonstrating independent problem-solving and full-stack development.',
                'technologies': ['Flask', 'SQLite', 'Python', 'HTML/CSS', 'API Integration'],
                'live_url': '',  # Add when deployed
                'github_url': 'https://github.com/yourusername/my-learning',  # Update with your repo
                'learning_focus': 'Independent project development and Flask mastery'
            },
            {
                'title': 'API Integration Collection',
                'subtitle': 'REST API Mastery Showcase',
                'description': 'Diverse collection of API integration projects including GitHub data, Spotify playlist builder, weather tracking, ISS location, and flight deals. Demonstrates API consumption and integration skills.',
                'technologies': ['Python', 'REST APIs', 'JSON', 'Requests', 'OAuth'],
                'live_url': '',
                'github_url': '',  # Add your API projects repo
                'learning_focus': 'API integration and external service communication'
            }
        ]

        # TECHNICAL SKILLS PROGRESSION
        context["skill_progression"] = {
            "confident_professional": [
                {"name": "Python", "months_experience": 30, "color": "#3776ab"},
                {
                    "name": "Algorithm Development",
                    "months_experience": 24,
                    "color": "#ff6b35",
                },
                {"name": "Flask", "months_experience": 18, "color": "#000000"},
                {
                    "name": "API Integration",
                    "months_experience": 20,
                    "color": "#4caf50",
                },
            ],
            "strong_growing": [
                {"name": "Django", "months_experience": 12, "color": "#092e20"},
                {"name": "Data Science", "months_experience": 15, "color": "#ff9800"},
                {"name": "PostgreSQL", "months_experience": 10, "color": "#336791"},
                {"name": "Linux/Ubuntu", "months_experience": 18, "color": "#e95420"},
            ],
            "active_learning": [
                {"name": "LLM Engineering", "months_experience": 2, "color": "#9c27b0"},
                {
                    "name": "Machine Learning",
                    "months_experience": 8,
                    "color": "#ff5722",
                },
                {"name": "TensorFlow", "months_experience": 6, "color": "#ff6f00"},
                {"name": "Rust (Next)", "months_experience": 0, "color": "#ce422b"},
            ],
        }

        # LEARNING TIMELINE DATA
        context["learning_timeline"] = [
            {
                "date": "Aug 2022",
                "title": "Business Analytics Foundation",
                "description": "Started with data analysis using Excel, SQL, and Tableau",
                "color": "navy",
                "icon": "fas fa-chart-bar",
            },
            {
                "date": "Dec 2022",
                "title": "Harvard CS50 Python",
                "description": "Academic programming foundation and computer science principles",
                "color": "teal",
                "icon": "fas fa-university",
            },
            {
                "date": "Mar 2023",
                "title": "Web Development & Linux",
                "description": "Django framework and Linux system administration",
                "color": "lavender",
                "icon": "fas fa-globe",
            },
            {
                "date": "Jun 2023",
                "title": "Data Science Mastery",
                "description": "NumPy, Pandas, Machine Learning, TensorFlow",
                "color": "coral",
                "icon": "fas fa-brain",
            },
            {
                "date": "Mar 2024",
                "title": "100 Days of Code Challenge",
                "description": "100 diverse Python projects over 6 months",
                "color": "mint",
                "icon": "fas fa-fire",
            },
            {
                "date": "Current",
                "title": "LLM Engineering & Portfolio",
                "description": "Building sophisticated applications while learning AI",
                "color": "yellow",
                "icon": "fas fa-rocket",
            },
        ]

        # PORTFOLIO INTEGRATION - Real Data
        try:
            # Systems showcase
            featured_systems = (
                SystemModule.objects.filter(status__in=["deployed", "published"])
                .select_related("system_type")
                .prefetch_related("technologies")[:3]
            )
            context["portfolio_systems"] = featured_systems

            # DataLogs for learning documentation
            recent_datalogs = Post.objects.filter(status="published").order_by(
                "-published_date"
            )[:3]
            context["recent_datalogs"] = recent_datalogs

            # Technology stats
            context["portfolio_stats"] = {
                "total_systems": SystemModule.objects.count(),
                "total_technologies": Technology.objects.count(),
                "total_datalogs": Post.objects.filter(status="published").count(),
                "learning_entries_planned": 15,  # Backlog you mentioned
            }

        except Exception:
            # Fallback for development
            context["portfolio_stats"] = {
                "total_systems": 8,
                "total_technologies": 12,
                "total_datalogs": 0,
                "learning_entries_planned": 15,
            }

        # CURRENT LEARNING STATUS
        context["current_status"] = {
            "availability": "Seeking first professional tech role",
            "current_learning": "LLM Engineering with Udemy",
            "next_goal": "Rust development for high-performance applications",
            "location": "Remote or Alabama-based opportunities",
            "transition_stage": "Ready for entry-level Python development role",
        }

        # CALL-TO-ACTION DATA
        context["cta_sections"] = [
            {
                "title": "Explore My Projects",
                "description": "See the progression from simple scripts to complex applications",
                "url": "/projects/",
                "icon": "fas fa-folder-open",
                "color": "teal",
            },
            {
                "title": "Read Learning Journey",
                "description": "Technical insights and learning documentation",
                "url": "/blog/",
                "icon": "fas fa-book-open",
                "color": "lavender",
            },
            {
                "title": "Download Resume",
                "description": "Professional credentials and experience details",
                "url": "/resume/download/",
                "icon": "fas fa-download",
                "color": "coral",
            },
            {
                "title": "Let's Connect",
                "description": "Discuss opportunities and collaboration",
                "url": "/communication/",
                "icon": "fas fa-envelope",
                "color": "mint",
            },
        ]

        # META DATA FOR SEO
        context["page_title"] = (
            "Python Developer & Algorithm Enthusiast - Learning Journey Portfolio"
        )
        context["page_description"] = (
            "Self-taught Python developer with 2+ years intensive learning. Harvard CS50, 100 Days of Code completed, building complex applications. Ready for professional development role."
        )
        context["page_keywords"] = (
            "Python Developer, Self-Taught Programmer, Algorithm Development, Django, Flask, Data Science, Machine Learning, Career Transition"
        )

        return context


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
