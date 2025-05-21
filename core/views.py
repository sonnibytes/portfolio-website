from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render

from .models import CorePage, Skill, Education, Experience, Contact, SocialLink

# If create contact form later uncomment below
# from .forms import ContactForm


class HomeView(TemplateView):
    """Home/Dashboard View."""
    template_name = 'core/index.html'

    # Get Skills data
    def get_queryset(self):
        pass  # May restructure skills models and change aggregation, maybe add skills to experience?

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = "Dashboard"
        context['project_count']
        context['post_count']
        context['experience_years']

        # Featured project.....

        # Recent Posts....


class DeveloperProfileView(TemplateView):
    """Dev profile/about page."""
    
    template_name = 'core/developer-profile.html'

    # Profile / Bio

    # Skills Hub

    # Education / Learning

    # Experience

    # Contact Methods - Link Up


class CommTerminalView(FormView):
    """Contact form styled as communication terminal."""
    template_name = 'core/communication.html'

    def get_context_data(self, **kwargs) -> dict[str, any]:
        context = super().get_context_data(**kwargs)
        context["profile"]
        return context
    
    def form_valid(self, form):
        # Temporarily using a placeholder for form processing
        # When you create the real form, you can uncomment this code

        # # Process the form data
        # name = form.cleaned_data['name']
        # email = form.cleaned_data['email']
        # subject = form.cleaned_data['subject']
        # message = form.cleaned_data['message']

        # # You could send an email here
        # # send_mail(subject, message, email, ['your@email.com'])

        # # Add a success message
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
    


def privacy(request):
    return render(request, "core/privacy.html")


def terms(request):
    return render(request, "core/terms.html")
