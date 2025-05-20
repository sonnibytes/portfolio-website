from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render


# If create a contact form later
# from .forms import ContactForm


class HomeView(TemplateView):
    """Home/Dashboard View."""
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add sample data for the initial view
        # Can replace this with real data from models later
        context["project_count"] = 6
        context["blog_count"] = 12

        # Featured project placeholder
        context["featured_project"] = {
            "title": "AI-Powered Data Analysis Platform",
            "description": "Real-time data processing system using Python, Django, and machine learning algorithms to analyze large datasets.",
            "technologies": [
                {"name": "Python"},
                {"name": "Django"},
                {"name": "TensorFlow"},
                {"name": "PostgreSQL"},
                {"name": "Docker"},
            ],
            "slug": "ai-data-analysis",
        }

        # Add recent posts
        context["recent_posts"] = [
            {
                "title": "Building Efficient Data Pipelines",
                "created_at": "2025-05-10",
                "slug": "building-data-pipelines",
            },
            {
                "title": "Django ORM Optimization Techniques",
                "created_at": "2025-05-05",
                "slug": "django-orm-optimization",
            },
            {
                "title": "Machine Learning Model Deployment",
                "created_at": "2025-04-28",
                "slug": "ml-model-deployment",
            },
        ]

        return context


class DeveloperProfileView(TemplateView):
    """Dev profile/about page."""
    template_name = 'core/developer_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Profile placeholder data
        context["profile"] = {
            "name": "Your Name",
            "title": "Python Developer",
            "bio": "Experienced Python developer specializing in Django web applications, data analysis, and machine learning integration. Passionate about creating efficient, scalable solutions to complex problems.",
            "location": "Birmingham, Alabama, US",
            "years_experience": 5,
            "specialties": [
                {"name": "Backend Development"},
                {"name": "Data Analysis"},
                {"name": "API Development"},
                {"name": "System Architecture"},
            ],
            "focus_areas": [
                {"name": "Python/Django Applications"},
                {"name": "Data Processing Systems"},
                {"name": "Machine Learning Integration"},
            ],
            "skills": [
                {"name": "Python", "proficiency": 95, "category": "languages"},
                {"name": "Django", "proficiency": 90, "category": "frameworks"},
                {"name": "JavaScript", "proficiency": 75, "category": "languages"},
                {"name": "SQL", "proficiency": 85, "category": "languages"},
                {"name": "React", "proficiency": 65, "category": "frameworks"},
                {"name": "Docker", "proficiency": 80, "category": "tools"},
                {"name": "AWS", "proficiency": 75, "category": "tools"},
                {"name": "Git", "proficiency": 90, "category": "tools"},
            ],
            "education": [
                {
                    "degree": "B.S. Computer Science",
                    "institution": "University of Alabama",
                    "year_start": 2018,
                    "year_end": 2022,
                },
                {
                    "degree": "Full Stack Web Development Bootcamp",
                    "institution": "Tech Academy",
                    "year_start": 2017,
                    "year_end": 2017,
                },
            ],
            "experience": [
                {
                    "position": "Senior Python Developer",
                    "company": "Tech Solutions Inc.",
                    "year_start": 2023,
                    "current": True,
                    "description": "Leading backend development team, building scalable data processing systems.",
                },
                {
                    "position": "Django Developer",
                    "company": "Web Innovations Co.",
                    "year_start": 2022,
                    "year_end": 2023,
                    "description": "Developed RESTful APIs and web applications using Django and Django REST Framework.",
                },
            ],
            "contact_methods": [
                {
                    "name": "GitHub",
                    "url": "https://github.com/yourusername",
                    "handle": "@yourusername",
                },
                {
                    "name": "LinkedIn",
                    "url": "https://linkedin.com/in/yourprofile",
                    "handle": "Your Name",
                },
                {
                    "name": "Email",
                    "url": "mailto:you@example.com",
                    "handle": "you@example.com",
                },
            ],
        }

        return context


class CommTerminalView(FormView):
    """Contact form styled as a communication terminal."""
    template_name = 'core/comm_terminal.html'
    # form_class = ContactForm # Uncomment when form is created
    success_url = reverse_lazy('contact')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add contact methods
        context["profile"] = {
            "contact_methods": [
                {
                    "name": "GitHub",
                    "url": "https://github.com/yourusername",
                    "handle": "@yourusername",
                },
                {
                    "name": "LinkedIn",
                    "url": "https://linkedin.com/in/yourprofile",
                    "handle": "Your Name",
                },
                {
                    "name": "Email",
                    "url": "mailto:you@example.com",
                    "handle": "you@example.com",
                },
            ],
        }

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