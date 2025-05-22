from django.views.generic import TemplateView, DetailView, FormView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from .models import CorePage, Skill, Education, Experience, SocialLink
from .forms import ContactForm
from blog.models import Post
from projects.models import SystemModule


class HomeView(TemplateView):
    """Home/Dashboard View."""
    template_name = 'core/index.html'

    # Get Skills data
    def get_queryset(self):
        pass  # May restructure skills models and change aggregation, maybe add skills to experience?

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get featured projects, limit 3
        context['featured_projects'] = SystemModule.objects.filter(
            status='published', featured=True
        ).order_by('-created')[:3]

        # Get latest blog posts, limit 3
        context['latest_posts'] = Post.objects.filter(
            status='published'
        ).order_by('-published_date')[:3]

        # Get skill categories for a quick overview
        context['skill_categories'] = Skill.objects.values_list(
            'category', flat=True
        ).distinct()

        context['title'] = "Dashboard"
        context['project_count']
        context['post_count']
        context['experience_years']

        return context


class DeveloperProfileView(TemplateView):
    """Dev profile/about page."""
    template_name = 'core/developer-profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get skills grouped by category
        skill_categories = {}
        for category, label in Skill.CATEGORY_CHOICES:
            skills = Skill.objects.filter(category=category).order_by("display_order")
            if skills.exists():
                skill_categories[category] = {"label": label, "skills": skills}
        context["skill_categories"] = skill_categories

        # Get education
        context["education"] = Education.objects.all()

        # Get work experience
        context["experiences"] = Experience.objects.all()

        # Get social links
        context["social_links"] = SocialLink.objects.all()

        return context


class CommTerminalView(FormView):
    """Contact form styled as communication terminal."""
    template_name = 'core/communication.html'
    form_class = ContactForm
    success_url = reverse_lazy('core:contact_success')

    def form_valid(self, form):
        # Save the contact submission
        form.save()
        # Add a success message
        messages.success(
            self.request,
            "TRANSMISSION_SUCCESSFUL: Your message has been received. Stand by for response.",
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, "TRANSMISSION_ERROR: Please check your input and try again."
        )
        return super().form_invalid(form)


class ContactSuccessView(TemplateView):
    """View for contact form submission success."""
    template_name = 'core/contact_success.html'


class CorePageView(DetailView):
    """Generic view for static pages stored in database."""
    model = CorePage
    template_name = 'core/page.html'
    context_object_name = "page"

    def get_queryset(self):
        # Only show published pages
        return CorePage.objects.filter(is_published=True)


class PrivacyView(TemplateView):
    """View for the privacy policy page."""
    template_name = 'core/privacy.html'


class TermsView(TemplateView):
    """View for the Terms of Service page."""
    template_name = "core/terms.html"


class ResumeView(TemplateView):
    """View for resume/CV page."""
    template_name = "core/resume.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['skills'] = Skill.objects.all().order_by('category', 'display_order')
        context['education'] = Education.objects.all()
        context['experiences'] = Experience.objects.all()
        return context


@method_decorator(csrf_protect, name='dispatch')
class ErrorView(TemplateView):
    """View for custom error pages."""
    template_name = 'core/error.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['error_code'] = kwargs.get('error_code', '404')
        context['error_message'] = kwargs.get('error_message', 'Page not found')
        return context
