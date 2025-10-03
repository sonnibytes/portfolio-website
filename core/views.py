from django.views.generic import TemplateView, DetailView, FormView, View
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, HttpResponseNotFound, HttpResponseServerError, HttpResponseForbidden, Http404
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from django.db.models import Count, Avg, Q
from django.template.loader import render_to_string, get_template
from django.conf import settings 
import os
import calendar
from collections import defaultdict
import json

from .models import CorePage, Skill, Education, Experience, SocialLink, Contact, LearningJourneyManager, PortfolioAnalytics, SkillTechnologyRelation
from .forms import ContactForm
from blog.models import Post, Category
from projects.models import SystemModule, Technology, LearningMilestone
from datetime import timedelta, datetime

# For PDF generation (install with: pip install reportlab weasyprint)
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False


class HomeView(TemplateView):
    """AURA Home/Dashboard View updated with learning-focused metrics."""

    template_name = "core/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ========== DYNAMIC LEARNING JOURNEY METRICS ==========
        journey_manager = LearningJourneyManager()
        context["learning_journey"] = journey_manager.get_journey_overview()

        # AURA System Metrics
        context["active_systems"] = SystemModule.objects.filter(
            status__in=["deployed", "published"]
        ).count() or 12

        # Systems in all statuses except draft and archived
        context["total_systems"] = SystemModule.objects.exclude(status__in=["draft", 'archived']).count()

        context["total_logs"] = Post.objects.filter(status="published").count() or 24

        context["technologies_count"] = Technology.objects.count() or 15

        # Featured systems (dynamic)
        featured_systems = SystemModule.objects.filter(
            featured=True
        ).exclude(status__in=['draft', 'archived']).select_related("system_type").prefetch_related("technologies")[:3]
        
        if not featured_systems.exists():
            # Fallback to top portfolio-ready systems
            featured_systems = SystemModule.objects.filter(
                portfolio_ready=True,
                status__in=["deployed", "published"]
            ).select_related("system_type").prefetch_related("technologies")[:3]

        context['featured_systems'] = featured_systems

        # Latest DataLogs (limit 3 for homepage)
        context["latest_posts"] = (
            Post.objects.filter(status="published")
            .select_related("category")
            .order_by("-published_date")[:3]
        )

        # Quick Stats for Dashboard Cards
        context["in_development"] = SystemModule.objects.filter(status="in_development").count() or 3

        context["recent_logs"] = (
            Post.objects.filter(
                status="published",
                published_date__gte=timezone.now() - timedelta(days=30),
            ).count()
        )

        # Categories for navigation
        context["categories"] = Category.objects.all()[:5]

        # Additional metrics for status display
        context["systems_testing"] = (
            SystemModule.objects.filter(status="testing").count() or 2
        )

        return context


class DeveloperProfileView(TemplateView):
    """
    Enhanced Developer Profile with Dynamic Learning Journey
    Updated to use new Skill-Technology relationship model
    """
    template_name = 'core/developer-profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ========== ENHANCED SKILL CATEGORIES WITH TECHNOLOGY RELATIONSHIPS ==========
        skill_categories = {}
        for category, label in Skill.CATEGORY_CHOICES:
            skills = Skill.objects.filter(category=category).prefetch_related(
                'technology_relations__technology',
                'project_gains__system'
            ).order_by('-proficiency', 'name')

            if skills.exists():
                # Enhance each skill with its tech relationships
                enhanced_skills = []
                for skill in skills:
                    # Get primary (strongest) technologies for this skill
                    primary_technologies = skill.technology_relations.filter(
                        strength__in=[3, 4]  # Essential Technology, Primary Implementation
                    ).select_related('technology').order_by('-strength')

                    # Get supporting technologies
                    supporting_technologies = skill.technology_relations.filter(
                        strength__in=[1, 2]  # Occasionally used, Commonly used
                    ).select_related('technology').order_by('-strength')

                    # Calcuclate skill-specific metrics
                    project_applications = skill.project_gains.count()
                    last_used = None
                    if skill.project_gains.exists():
                        last_used = skill.project_gains.order_by('-system__created_at').first().system.created_at

                    # Try to get mastery progression score, fallback to simple calculation
                    try:
                        mastery_score = skill.get_mastery_progression_score()
                    except AttributeError:
                        mastery_score = skill.proficiency * 20

                    enhanced_skills.append({
                        'skill': skill,
                        'primary_technologies': primary_technologies,
                        'supporting_technologies': supporting_technologies,
                        'total_tech_count': skill.technology_relations.count(),
                        'project_applications': project_applications,
                        'last_used': last_used,
                        'mastery_score': mastery_score,
                    })

                skill_categories[category] = {
                    "label": label,
                    "skills": enhanced_skills,
                    "skill_count": len(enhanced_skills),
                    "mastery_count": len([s for s in enhanced_skills if s['skill'].proficiency >= 4]),
                    "learning_count": len([s for s in enhanced_skills if getattr(s['skill'], 'is_currently_learning', False)]),
                    "avg_proficiency": sum(s['skill'].proficiency for s in enhanced_skills) / len(enhanced_skills) if enhanced_skills else 0,
                    "total_technologies": sum(s['total_tech_count'] for s in enhanced_skills),
                }
        context["skill_categories"] = skill_categories

        # ========== TECHNOLOGY-SKILL RELATIONSHIP OVERVIEW ==========
        # Get the most connected techs (techs used w many skills)
        top_technologies = Technology.objects.annotate(
            skill_connections=Count('skill_relations'),
            primary_skill_connections=Count('skill_relations', filter=Q(skill_relations__strength__in=[3, 4]))
        ).filter(skill_connections__gt=0).order_by('-primary_skill_connections', '-skill_connections')[:8]

        context["top_technologies"] = [{
            'technology': tech,
            'total_connections': tech.skill_connections,
            'primary_connections': tech.primary_skill_connections,
            'supporting_connections': tech.skill_connections - tech.primary_skill_connections,
        } for tech in top_technologies]

        # ========== SKILL LEARNING PROGRESSION ANALYSIS ==========
        # Get skills by learning timeline if available
        skills_with_timeline = []
        for skill in Skill.objects.all():
            try:
                timeline = skill.get_learning_timeline_events()
                if timeline:
                    skills_with_timeline.append({
                        'skill': skill,
                        'first_learned': min(event['date'] for event in timeline),
                        'latest_application': max(event['date'] for event in timeline),
                        'learning_events': len(timeline),
                        'progression_score': skill.get_mastery_progression_score() if hasattr(skill, 'get_mastery_progression_score') else skill.proficiency * 20,
                    })
            except AttributeError:
                # Skip if skill doesn't have timeline methods
                pass
        
        # Sort by learning progression
        skills_with_timeline.sort(key=lambda x: x['progression_score'], reverse=True)
        context["learning_progression_skills"] = skills_with_timeline[:10]  # Top 10 most developed

        # ========== SKILL-TECHNOLOGY RELATIONSHIP INSIGHTS ==========
        # Calculate relationship type distribution
        relationship_stats = defaultdict(int)

        for relation in SkillTechnologyRelation.objects.all():
            relationship_stats[relation.relationship_type] += 1
        
        context["relationship_insights"] = {
            'total_relationships': SkillTechnologyRelation.objects.count(),
            'relationship_types': dict(relationship_stats),
            'avg_strength': SkillTechnologyRelation.objects.aggregate(
                avg_strength=Avg('strength')
            )['avg_strength'] or 0,
            'strong_relationships': SkillTechnologyRelation.objects.filter(strength__in=[3, 4]).count(),
        }

        # Educational background w learning context
        education_with_skills = []
        for edu in Education.objects.all().order_by('-end_date'):
            # Try to get learning summary and skills with fallbacks
            try:
                summary = edu.get_learning_summary()
            except AttributeError:
                summary = {}
            
            try:
                skills_gained = edu.skills_learned.all()[:5]
            except AttributeError:
                skills_gained = []
            

            education_with_skills.append({
                'education': edu,
                'summary': summary,
                'skills_gained': skills_gained,
            })
        context['education_enhanced'] = education_with_skills

        # Professional experience
        context["experiences"] = Experience.objects.all().order_by('-end_date', '-start_date')

        # Social/Network links
        context["social_links"] = SocialLink.objects.all().order_by('display_order')

        # Dynamic Portfolio Metrics using LearningJourneyManager
        try:
            journey_manager = LearningJourneyManager()
            learning_overview = journey_manager.get_journey_overview()
        except (AttributeError, NameError):
            # Fallback if LearningJourneyManager is not available
            learning_overview = {
                'systems_built': SystemModule.objects.count(),
                'current_projects': SystemModule.objects.filter(status='in_development').count(),
                'duration_years': '2+',
                'skills_mastered': Skill.objects.filter(proficiency__gte=4).count(),
                'certificates_earned': 6,
                'learning_hours': '500+',
            }

        context["portfolio_metrics"] = {
            'total_systems': learning_overview['systems_built'],
            'systems_completed': SystemModule.objects.deployed().count(),
            'systems_in_progress': learning_overview['current_projects'],
            'total_logs_count': Post.objects.filter(status='published').count(),
            'technologies_mastered': Technology.objects.count(),
            'languages_used': Technology.objects.filter(category='language').count(),
            'learning_years': learning_overview['duration_years'],
            'skills_mastered': learning_overview['skills_mastered'],
            'certificates_earned': learning_overview['certificates_earned'],
            'learning_hours': learning_overview['learning_hours'],
            'skill_technology_connections': SkillTechnologyRelation.objects.count(),
            'primary_tech_relationships': SkillTechnologyRelation.objects.filter(strength__in=[3, 4]).count(),
        }

        # Recent Activity Timeline (dynamic)
        context["recent_systems"] = SystemModule.objects.filter(
            status__in=["deployed", "published"]
        ).select_related('system_type').order_by("-created_at")[:3]

        context["recent_posts"] = Post.objects.filter(status="published").order_by(
            "-published_date"
        )[:3]

        # Technology breakdown by category (dynamic) - Enhanced w skill connections
        context["tech_by_category"] = {}
        for category, label in Technology.CATEGORY_CHOICES:
            techs = (
                Technology.objects.filter(category=category)
                .annotate(
                    system_count=Count("systems"),
                    skill_connections=Count('skill_relations')
                ).order_by("-skill_connections", "-system_count")
            )
            if techs.exists():
                context["tech_by_category"][category] = {
                    "label": label,
                    "technologies": techs[:8],  # Top 8 most used
                }

        # Enhanced Learning progression summary w skill-tech relationships
        context["learning_progression"] = {
            'skills_categories': len(skill_categories),
            'total_skills': Skill.objects.count(),
            'mastered_skills': Skill.objects.filter(proficiency__gte=4).count(),
            'learning_skills': Skill.objects.filter(is_currently_learning=True).count() if hasattr(Skill, 'is_currently_learning') else 0,
            'portfolio_ready_projects': SystemModule.objects.filter(portfolio_ready=True).count() if hasattr(SystemModule, 'portfolio_ready') else 0,
            'total_technologies': Technology.objects.count(),
            'skill_tech_relationships': SkillTechnologyRelation.objects.count(),
            'strong_relationships': SkillTechnologyRelation.objects.filter(strength__in=[3, 4]).count(),
            'learning_milestones': LearningMilestone.objects.count() if LearningMilestone else 0,
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
    """
    AURA Communication Terminal - Enhanced Contact Interface.
    Captures user-submitted data + request metadata automatically.
    """
    template_name = 'core/communication.html'
    form_class = ContactForm
    success_url = reverse_lazy('core:contact_success')

    def get_client_ip(self, request):
        """
        Extract client IP address from request.
        Handles proxies and load balancers properly.

        Best Practice: Check X-Forwarded-For header first (for proxies),
        then fall back to REMOTE_ADDR.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # X-Forwarded-For can contain multiple IPs, first one is client
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_user_agent(self, request):
        """
        Extract user agent string from request.

        Best Practice: Get from HTTP_USER_AGENT header.
        Returns empty string if not avail.
        """
        return request.META.get('HTTP_USER_AGENT', '')
    
    def get_referrer(self, request):
        """
        Extract referrer/referring page from reuqest.

        Best Practice: Check HTTP_REFERER header.
        Note: 'Referer' intentionally mispelled in HTTP spec.
        """
        return request.META.get('HTTP_REFERER', '')
    
    def categorize_inquiry(self, form_data):
        """
        Automatically categorize inquiry based on subject/message content.

        Best Practice: Simple keyword matching for initial categorization.
        Can be reviewed/changed by admin later.
        """
        subject = form_data.get('subject', '').lower()
        message = form_data.get('message', '').lower()
        combined = f"{subject} {message}"

        # Keyword-based categorization
        if any(word in combined for word in ['hire', 'hiring', 'job', 'position', 'opportunity', 'employment']):
            return 'hiring'
        elif any(word in combined for word in ['project', 'build', 'develop', 'create']):
            return 'project'
        elif any(word in combined for word in ['collaborate', 'partnership', 'work together', 'team up']):
            return 'collaboration'
        elif any(word in combined for word in ['feedback', 'suggestion', 'improve']):
            return 'feedback'
        elif any(word in combined for word in ['question', 'how', 'what', 'why', 'when']):
            return 'question'
        else:
            return 'other'
        
    def determine_priority(self, form_data):
        """
        Automatically determine priority based on content.
        
        Best Practice: Conservative priority assignment.
        Most messages start as 'normal', can be escalated by admin.
        """
        subject = form_data.get('subject', '').lower()
        message = form_data.get('message', '').lower()
        combined = f"{subject} {message}"

        # Check for urgent keywords
        urgent_keywords = ['urgent', 'asap', 'immediately', 'emergency', 'critical']
        if any(keyword in combined for keyword in urgent_keywords):
            return 'high'  # Start at high, admin can escalate to urgent if needed
        
        # Check for high priority indicators
        high_priority_keywords = ['hiring', 'job offer', 'deadline', 'time-sensitive']
        if any(keyword in combined for keyword in high_priority_keywords):
            return 'high'
        
        # Default to normal priority
        return 'normal'

    def form_valid(self, form):
        """
        Save form with additional metadata.
        
        Best Practice: Don't modify the form's save() method.
        Instead, save with commit=False, add metadata, then save.
        """

        # Save the contact submission but don't commit to db yet
        contact = form.save(commit=False)

        # Add request metadata(Best Practice: Capture at submission time)
        contact.ip_address = self.get_client_ip(self.request)
        contact.user_agent = self.get_user_agent(self.request)
        contact.referrer_page = self.get_referrer(self.request)

        # Auto-Categorize and prioritize
        contact.inquiry_category = self.categorize_inquiry(form.cleaned_data)
        contact.priority = self.determine_priority(form.cleaned_data)

        # Set initial status flags (Best Practice: Set defaults explicitly)
        contact.is_read = False
        contact.response_sent = False
        contact.response_date = None

        # Now save to db
        contact.save()


        # Add AURA-themed success message
        messages.success(
            self.request,
            f"✓ TRANSMISSION_COMPLETE: Message #{contact.id:04d} received and logged. "
            f"Response protocol initiated. Expected delivery: 24-48 hours."
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Handle form validation errors with debugging.
        
        Best Practice: Log errors for debugging but show user-friendly messages.
        """
        # Debug logging (in production, use proper logging)
        print(f"🔴 CONTACT FORM VALIDATION FAILED")
        print(f"🔴 Errors: {form.errors}")
        print(f"🔴 Non-field errors: {form.non_field_errors()}")
        
        # User-friendly error message
        messages.error(
            self.request,
            "⚠ TRANSMISSION_ERROR: Data validation failed. "
            "Please verify all required fields are completed correctly."
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """Add terminal HUD context data."""
        context = super().get_context_data(**kwargs)

        # Add social links for network connections
        try:
            context['social_links'] = SocialLink.objects.all().order_by('display_order')
        except Exception:
            context['social_links'] = []
        
        # Professional Links - w error handling
        context['pro_links'] = {}
        try:
            github = SocialLink.objects.filter(name__iexact='github').first()
            if github:
                context['pro_links']['github'] = github
        except Exception:
            pass
            
        try:
            linkedin = SocialLink.objects.filter(name__iexact='linkedin').first()
            if linkedin:
                context['pro_links']['linkedin'] = linkedin
        except Exception:
            pass


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


# ======================  CUSTOM ERROR VIEWS ==================


def custom_404_view(request, exception):
    """Custom 404 error page with AURA theme"""
    context = {
        'request_path': request.path,
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'timestamp': timezone.now(),
    }
    return HttpResponseNotFound(render(request, 'errors/404.html', context).content)


def custom_500_view(request):
    """Custom 500 error page w AURA theme"""
    context = {
        'request_path': request.path,
        'timestamp': timezone.now(),
    }
    return HttpResponseServerError(render(request, 'errors/500.html', context).content)


def custom_403_view(request, exception):
    """Custom 403 error page w AURA theme"""
    context = {
        'request_path': request.path,
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'timestamp': timezone.now(),
    }
    return HttpResponseForbidden(render(request, 'errors/403.html', context).content)


# # Temp views to test error pages
# def test_500(request):
#     raise Exception("Test 500 error")


# from django.core.exceptions import PermissionDenied


# def test_403(request):
#     raise PermissionDenied("Test 403 Error")


# ============= ENHANCED DOWNLOAD RESUME VIEWS ==================
# Will hopefully replace previous resume download views

class EnhancedResumeDownloadView(TemplateView):
    """
    Modern resume download system with multiple format options
    Integrates with new skill-technology relationship model
    """
    
    def get(self, request, *args, **kwargs):
        format_type = kwargs.get("format", "pdf")

        # Track download for analytics
        self.track_download(format_type)

        if format_type == "pdf":
            return self.generate_pdf_resume()
        elif format_type == "json":
            return self.generate_json_resume()
        elif format_type == "txt":
            return self.generate_text_resume()
        elif format_type == "html":
            return self.generate_html_resume()
        else:
            return self.serve_static_resume()
        
    
    def track_download(self, format_type):
        """Track resume downloads for analytics"""
        try:
            from .models import PortfolioAnalytics
            today = timezone.now().date()
            analytics, created = PortfolioAnalytics.objects.get_or_create(date=today)
            analytics.resume_downloads += 1
            analytics.save()
        except (ImportError, AttributeError):
            # Analytics model not available
            pass

    def get_resume_data(self):
        """Gather all resume data from models"""
        
        # Personal info
        # TODO: Update site, email, phone info
        personal_info = {
            'name': 'Sonni Gunnels',
            'title': 'Python Developer',
            'subtitle': 'EHS Professional Transitioning to Software Development',
            'email': 'hello@aura.com',
            'website': 'https://sonnis-aura.com',
            'location': 'Raleigh, NC',
            'phone': None, 
        }


        # Professional summary with learning journey focus
        summary = """Self-motivated Python developer with 2+ years of intensive learning experience, 
        transitioning from EHS compliance to software development. Demonstrated technical growth through 
        progressive projects including this portfolio site, data analysis applications, and web development. 
        Brings analytical thinking, problem-solving skills, and attention to detail from compliance background. 
        Ready to contribute technical abilities while continuing to learn in a professional environment."""

        # Enhanced skill w technology relationships
        skills_by_category = {}
        for category, label in Skill.CATEGORY_CHOICES:
            skills = Skill.objects.filter(category=category).prefetch_related(
                'technology_relations__technology'
            ).order_by('-proficiency', 'name')

            if skills.exists():
                skills_data = []
                for skill in skills:
                    # Get primary technologies for this skill
                    primary_techs = skill.technology_relations.filter(
                        strength__in=[3, 4]
                    ).select_related('technology')

                    skills_data.append({
                        'name': skill.name,
                        'proficiency': skill.proficiency,
                        'proficiency_text': f'Level {skill.proficiency}/5',
                        'technologies': [rel.technology.name for rel in primary_techs],
                        'description': skill.description,
                        'is_learning': getattr(skill, 'is_currently_learning', False),
                    })

                skills_by_category[category] = {
                    'label': label,
                    'skills': skills_data
                }

        # Portfolio projects (most impressive ones)
        portfolio_projects = []
        projects = SystemModule.objects.filter(
            portfolio_ready=True
        ).prefetch_related('technologies').order_by('-created_at')[:6]

        for project in projects:
            portfolio_projects.append({
                'name': project.title,
                'description': project.description[:200] + "..." if len(project.description) > 200 else project.description,
                'technologies': [tech.name for tech in project.technologies.all()],
                'github_url': project.github_url,
                'live_url': project.live_url,
                'completion_date': project.created_at.strftime("%Y-%m") if project.created_at else None,
                'status': project.get_status_display(),
            })

        # Education with skills developed
        education_data = []
        for edu in Education.objects.all().order_by('-end_date'):
            education_data.append({
                'institution': edu.institution,
                'degree': edu.degree,
                'field': edu.field_of_study,
                'start_date': edu.start_date.strftime("%Y-%m") if edu.start_date else None,
                'end_date': edu.end_date.strftime("%Y-%m") if edu.end_date else "Present",
                'description': edu.description,
                'is_current': edu.is_current if hasattr(edu, 'is_current') else False,
            })
        
        # Professional experience
        experience_data = []
        for exp in Experience.objects.all().order_by('-end_date', '-start_date'):
            experience_data.append({
                'company': exp.company,
                'position': exp.position,
                'location': exp.location,
                'start_date': exp.start_date.strftime("%Y-%m") if exp.start_date else None,
                'end_date': exp.end_date.strftime("%Y-%m") if exp.end_date else "Present",
                'description': exp.description,
                'technologies': exp.get_technologies_list() if hasattr(exp, 'get_technologies_list') else [],
                'is_current': exp.is_current,
            })
        
        # Social Links
        social_links = []
        for link in SocialLink.objects.all().order_by('display_order'):
            social_links.append({
                'name': link.name,
                'url': link.url,
                'handle': getattr(link, 'handle', ''),
            })
        
        # Key Metrics
        metrics = {
            'total_skills': Skill.objects.count(),
            'mastered_skills': Skill.objects.filter(proficiency__gte=4).count(),
            'total_projects': SystemModule.objects.count(),
            'portfolio_projects': SystemModule.objects.filter(portfolio_ready=True).count(),
            'blog_posts': Post.objects.filter(status='published').count(),
            'technologies': Technology.objects.count(),
            'skill_tech_relationships': SkillTechnologyRelation.objects.count(),
        }
        
        return {
            'personal_info': personal_info,
            'summary': summary,
            'skills_by_category': skills_by_category,
            'portfolio_projects': portfolio_projects,
            'education': education_data,
            'experience': experience_data,
            'social_links': social_links,
            'metrics': metrics,
            'generated_date': datetime.now().strftime("%B %Y"),
        }

    def generate_pdf_resume(self):
        """Generate dynamic PDF resume"""
        if WEASYPRINT_AVAILABLE:
            return self.generate_pdf_with_weasyprint()
        elif REPORTLAB_AVAILABLE:
            return self.generate_pdf_with_reportlab()
        else:
            return self.serve_static_resume()

    def generate_pdf_with_weasyprint(self):
        """Generate PDF using WeasyPrint (HTML to PDF)"""
        try:
            resume_data = self.get_resume_data()

            # Render HTML template
            template = get_template('core/resume_pdf.html')
            html_content = template.render(resume_data)

            # Generate PDF
            pdf = weasyprint.HTML(string=html_content, base_url=self.request.build_absolute_uri())
            pdf_content = pdf.write_pdf()

            # Create response
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Sonni_Gunnels_Resume_{datetime.now().strftime("%Y_%m")}.pdf"'

            return response
        
        except Exception as e:
            return self.generate_pdf_with_reportlab()  # Fallback

    def generate_pdf_with_reportlab(self):
        """Generate PDF using ReportLab (programmatic)"""
        try:
            resume_data = self.get_resume_data()

            # Create response
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Sonni_Gunnels_Resume_{datetime.now().strftime("%Y_%m")}.pdf"'

            # Create PDF document
            doc = SimpleDocTemplate(response, pagesize=letter, topMargin=0.5*inch)
            story = []
            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#00BCD4'),
                spaceAfter=12,
                alignment=1  # Center
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#2C3E50'),
                spaceAfter=12,
                borderWidth=1,
                borderColor=colors.HexColor('#00BCD4'),
                borderPadding=5,
            )
            
            # Add content
            personal = resume_data['personal_info']
            
            # Header
            story.append(Paragraph(personal['name'], title_style))
            story.append(Paragraph(personal['title'], styles['Normal']))
            story.append(Paragraph(f"{personal['email']} | {personal['website']}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Summary
            story.append(Paragraph("Professional Summary", heading_style))
            story.append(Paragraph(resume_data['summary'], styles['Normal']))
            story.append(Spacer(1, 15))
            
            # Technical Skills
            story.append(Paragraph("Technical Skills", heading_style))
            for category, data in resume_data['skills_by_category'].items():
                story.append(Paragraph(f"<b>{data['label']}</b>", styles['Heading3']))
                for skill in data['skills'][:5]:  # Top 5 per category
                    skill_text = f"• {skill['name']} ({skill['proficiency_text']})"
                    if skill['technologies']:
                        skill_text += f" - {', '.join(skill['technologies'][:3])}"
                    story.append(Paragraph(skill_text, styles['Normal']))
                story.append(Spacer(1, 10))
            
            # Portfolio Projects
            if resume_data['portfolio_projects']:
                story.append(Paragraph("Portfolio Projects", heading_style))
                for project in resume_data['portfolio_projects'][:4]:  # Top 4 projects
                    story.append(Paragraph(f"<b>{project['name']}</b>", styles['Heading3']))
                    story.append(Paragraph(project['description'], styles['Normal']))
                    if project['technologies']:
                        story.append(Paragraph(f"Technologies: {', '.join(project['technologies'])}", styles['Normal']))
                    story.append(Spacer(1, 10))
            
            # Education
            if resume_data['education']:
                story.append(Paragraph("Education", heading_style))
                for edu in resume_data['education']:
                    story.append(Paragraph(f"<b>{edu['degree']}</b> - {edu['institution']}", styles['Heading3']))
                    date_range = f"{edu['start_date']} to {edu['end_date']}"
                    story.append(Paragraph(date_range, styles['Normal']))
                    if edu['description']:
                        story.append(Paragraph(edu['description'], styles['Normal']))
                    story.append(Spacer(1, 10))
            
            # Experience
            if resume_data['experience']:
                story.append(Paragraph("Professional Experience", heading_style))
                for exp in resume_data['experience']:
                    story.append(Paragraph(f"<b>{exp['position']}</b> - {exp['company']}", styles['Heading3']))
                    date_range = f"{exp['start_date']} to {exp['end_date']}"
                    story.append(Paragraph(date_range, styles['Normal']))
                    story.append(Paragraph(exp['description'], styles['Normal']))
                    story.append(Spacer(1, 10))
            
            # Build PDF
            doc.build(story)
            return response
            
        except Exception as e:
            return self.serve_static_resume()  # Final fallback

    def generate_json_resume(self):
        """Generate JSON Resume format"""
        try:
            resume_data = self.get_resume_data()
            personal = resume_data['personal_info']
            
            # JSON Resume Schema format
            json_resume = {
                "basics": {
                    "name": personal['name'],
                    "label": personal['title'],
                    "email": personal['email'],
                    "website": personal['website'],
                    "summary": resume_data['summary'],
                    "location": {
                        "city": "Raleigh",
                        "region": "North Carolina",
                        "countryCode": "US"
                    },
                    "profiles": [
                        {
                            "network": link['name'],
                            "url": link['url'],
                            "username": link.get('handle', '')
                        }
                        for link in resume_data['social_links']
                    ]
                },
                "work": [
                    {
                        "company": exp['company'],
                        "position": exp['position'],
                        "startDate": exp['start_date'],
                        "endDate": exp['end_date'] if exp['end_date'] != "Present" else None,
                        "summary": exp['description'],
                        "highlights": exp.get('technologies', [])
                    }
                    for exp in resume_data['experience']
                ],
                "education": [
                    {
                        "institution": edu['institution'],
                        "studyType": edu['degree'],
                        "area": edu['field'],
                        "startDate": edu['start_date'],
                        "endDate": edu['end_date'] if edu['end_date'] != "Present" else None,
                        "summary": edu['description']
                    }
                    for edu in resume_data['education']
                ],
                "skills": [],
                "projects": [
                    {
                        "name": proj['name'],
                        "description": proj['description'],
                        "highlights": proj['technologies'],
                        "url": proj.get('live_url') or proj.get('github_url'),
                        "roles": ["Developer"],
                        "entity": "Personal Project",
                        "type": "application"
                    }
                    for proj in resume_data['portfolio_projects']
                ],
                "meta": {
                    "canonical": f"{personal['website']}/resume.json",
                    "version": "v1.0.0",
                    "lastModified": datetime.now().isoformat(),
                    "generated_by": "AURA Portfolio System"
                }
            }
            
            # Add skills by category
            for category, data in resume_data['skills_by_category'].items():
                for skill in data['skills']:
                    json_resume['skills'].append({
                        "name": skill['name'],
                        "level": skill['proficiency_text'],
                        "keywords": skill['technologies']
                    })
            
            response = JsonResponse(json_resume, json_dumps_params={"indent": 2})
            response['Content-Disposition'] = f'attachment; filename="sonni_gunnels_resume_{datetime.now().strftime("%Y_%m")}.json"'
            
            return response
            
        except Exception as e:
            return JsonResponse({"error": "JSON resume generation failed"}, status=500)

    def generate_text_resume(self):
        """Generate plain text resume"""
        try:
            resume_data = self.get_resume_data()
            personal = resume_data['personal_info']
            
            text_content = f"""
{personal['name'].upper()}
{personal['title']}
{personal['email']} | {personal['website']}
{personal['location']}

PROFESSIONAL SUMMARY
{resume_data['summary']}

TECHNICAL SKILLS
"""
            
            for category, data in resume_data['skills_by_category'].items():
                text_content += f"\n{data['label'].upper()}\n"
                for skill in data['skills'][:5]:
                    tech_list = ", ".join(skill['technologies'][:3]) if skill['technologies'] else ""
                    text_content += f"• {skill['name']} ({skill['proficiency_text']})"
                    if tech_list:
                        text_content += f" - {tech_list}"
                    text_content += "\n"
            
            if resume_data['portfolio_projects']:
                text_content += "\nPORTFOLIO PROJECTS\n"
                for project in resume_data['portfolio_projects'][:4]:
                    text_content += f"\n{project['name']}\n"
                    text_content += f"{project['description']}\n"
                    if project['technologies']:
                        text_content += f"Technologies: {', '.join(project['technologies'])}\n"
            
            if resume_data['education']:
                text_content += "\nEDUCATION\n"
                for edu in resume_data['education']:
                    text_content += f"\n{edu['degree']} - {edu['institution']}\n"
                    text_content += f"{edu['start_date']} to {edu['end_date']}\n"
                    if edu['description']:
                        text_content += f"{edu['description']}\n"
            
            if resume_data['experience']:
                text_content += "\nPROFESSIONAL EXPERIENCE\n"
                for exp in resume_data['experience']:
                    text_content += f"\n{exp['position']} - {exp['company']}\n"
                    text_content += f"{exp['start_date']} to {exp['end_date']}\n"
                    text_content += f"{exp['description']}\n"
            
            response = HttpResponse(text_content, content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="sonni_gunnels_resume_{datetime.now().strftime("%Y_%m")}.txt"'
            
            return response
            
        except Exception as e:
            return HttpResponse("Text resume generation failed", content_type='text/plain', status=500)

    def generate_html_resume(self):
        """Generate standalone HTML resume"""
        try:
            resume_data = self.get_resume_data()
            template = get_template('core/resume_download.html')
            html_content = template.render(resume_data)

            response = HttpResponse(html_content, content_type='text/html')
            response['Content-Disposition'] = f'attachment; filename="sonni_gunnels_resume_{datetime.now().strftime("%Y_%m")}.html"'
            
            return response
            
        except Exception as e:
            return HttpResponse("<h1>HTML resume generation failed</h1>", content_type='text/html', status=500)

    def serve_static_resume(self):
        """Serve static PDF file as fallback"""
        try:
            static_paths = [
                os.path.join(settings.STATIC_ROOT or "", "docs", "sonni_gunnels_resume.pdf"),
                os.path.join(settings.BASE_DIR, "static", "docs", "sonni_gunnels_resume.pdf"),
                os.path.join(settings.BASE_DIR, "staticfiles", "docs", "sonni_gunnels_resume.pdf"),
            ]
            
            for path in static_paths:
                if os.path.exists(path):
                    with open(path, 'rb') as pdf_file:
                        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                        response['Content-Disposition'] = 'attachment; filename="Sonni_Gunnels_Resume.pdf"'
                        return response
            
            # If no static file found, create a simple message
            return JsonResponse({
                "message": "Resume temporarily unavailable. Please contact directly.",
                "contact_url": reverse('core:contact'),
                "email": "hello@mldevlog.com"
            })
            
        except Exception as e:
            raise Http404("Resume not available")


class ResumePreviewView(TemplateView):
    """
    Show resume content on webpage (for preview/sharing)
    """
    template_name = 'core/resume_preview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the same resume data used for downloads
        download_view = EnhancedResumeDownloadView()
        resume_data = download_view.get_resume_data()

        context.update(resume_data)
        context['page_title'] = 'Resume - Sonni Gunnels'
        context['is_preview'] = True

        return context


# API View for Resume Download Tracking
class TrackDownloadAPIView(View):
    """API endpoint for tracking resume downloads"""

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            format_type = data.get('format', 'unknown')
            timestamp = data.get('timestamp')

            # Track in analytics if available
            try:
                from .models import PortfolioAnalytics
                today = timezone.now().date()
                analytics, created = PortfolioAnalytics.objects.get_or_create(date=today)
                analytics.resume_downloads += 1
                analytics.save()
            except (ImportError, AttributeError):
                pass

            return JsonResponse({'status': 'tracked', 'format': format_type})
        
        except Exception as e:
            return JsonResponse({'error': 'tracking failed'}, status=400)