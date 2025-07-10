"""
Core Admin Forms - Complete CRUD Support
Handles: CorePage, Skill, Education, EducationSkillDevelopment, Experience, Contact, SocialLink, PortfolioAnalytics
Version 3.0 - Based on Actual Core Models
"""
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.text import slugify

from datetime import date

from .models import Contact, CorePage, Skill, Education, Experience, PortfolioAnalytics, EducationSkillDevelopment, SocialLink
from markdownx.fields import MarkdownxFormField  # pyright: ignore[reportMissingImports]


# Existing Contact Form
# class ContactForm(forms.ModelForm):
#     """Form for user contact submissions."""

#     class Meta:
#         model = Contact
#         fields = ['name', 'email', 'subject', 'message']
#         widget = {
#             'name': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Your Name'
#             }),
#             'email': forms.EmailInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'your.email@example.com'
#             }),
#             'subject': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Message Subject'
#             }),
#             'message': forms.Textarea(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Your message here...',
#                 'rows': 5
#             }),
#         }


class CorePageForm(forms.ModelForm):
    """Enhanced core page form w Markdownx support."""
    content = MarkdownxFormField()

    class Meta:
        model = CorePage
        fields = ['title', 'slug', 'content', 'meta_description', 'is_published']
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Page Title"}
            ),
            "slug": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "auto-generated-from-title",
                }
            ),
            "meta_description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "SEO meta description (160 characters max)",
                    "maxlength": 160,
                }
            ),
            "is_published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_slug(self):
        """Auto-generate slug from title if not provided."""
        slug = self.cleaned_data.get('slug')
        title = self.cleaned_data.get('title')

        if not slug and title:
            slug = slugify(title)
        
        # Check for uniqueness
        if slug:
            existing = CorePage.objects.filter(slug=slug)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError(f"A page with slug '{slug}' already exists.")
        
        return slug


class SkillForm(forms.ModelForm):
    """Enhanced skill form with technology relationship support."""

    class Meta:
        model = Skill
        fields = [
            'name',
            'slug',
            'category',
            'description',
            'proficiency',
            'years_experience',
            'last_used',
            'is_currently_learning',
            'is_certified',
            'icon',
            'color',
            'display_order',
            'is_featured',
            'related_technology'
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Skill Name (e.g., Python, Django, React)",
                }
            ),
            "slug": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "auto-generated-from-name",
                }
            ),
            "category": forms.Select(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Skill description",
                }
            ),
            "proficiency": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "icon": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "fa-python (FontAwesome icon name)",
                }
            ),
            "color": forms.TextInput(attrs={"class": "form-control", "type": "color"}),
            "display_order": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
            "related_technology": forms.Select(attrs={"class": "form-control"}),
            "years_experience": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "max": 50, "step": 0.5}
            ),
            "is_featured": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "last_used": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "is_currently_learning": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "is_certified": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate related_technology choices
        try:
            from projects.models import Technology
            self.fields['related_technology'].queryset = Technology.objects.all()
            self.fields['related_technology'].empty_label = "Select related technology..."
        except ImportError:
            # If projects app isn't available, hide the field
            self.fields['related_technology'].widget = forms.HiddenInput()
    
    def clean_slug(self):
        """Auto-generate slug from name if not provided."""
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')

        if not slug and name:
            slug = slugify(name)
        
        # Check for uniqueness
        if slug:
            existing = Skill.objects.filter(slug=slug)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError(f"A skill with slug '{slug}' already exists.")
        
        return slug
    
    def clean_years_experience(self):
        """Validate years experience is reasonable."""
        years = self.cleaned_data.get('years_experience')
        if years and years > 30:
            raise ValidationError("Years of experience seems unusually high..")
        return years


class EducationForm(forms.ModelForm):
    """Enhanced education form with skill and project relationships."""

    class Meta:
        model = Education
        fields = [
            'institution',
            'slug',
            'degree',
            'field_of_study',
            'start_date',
            'end_date',
            'description',
            'is_current',
            'learning_type',
            'platform',
            'certificate_url',
            'hours_completed',
            'related_systems',
            'learning_intensity',
            'career_relevance'
        ]

        widgets = {
            "institution": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Institution/Platform Name",
                }
            ),
            "slug": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "auto-generated-from-degree-institution",
                }
            ),
            "degree": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Degree/Certification/Course Name",
                }
            ),
            "field_of_study": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Field of Study/Subject Area",
                }
            ),
            "start_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "end_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe what you learned and achieved...",
                }
            ),
            "is_current": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "learning_type": forms.Select(attrs={"class": "form-control"}),
            "platform": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., edX HarvardX, Udemy, University of Alabama",
                }
            ),
            "certificate_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://link-to-certificate.com",
                }
            ),
            "hours_completed": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "placeholder": "Total hours of instruction/study",
                }
            ),
            "related_systems": forms.SelectMultiple(
                attrs={"class": "form-control", "size": 4}
            ),
            "learning_intensity": forms.Select(attrs={"class": "form-control"}),
            "career_relevance": forms.Select(attrs={"class": "form-control"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate related_systems choices
        try:
            from projects.models import SystemModule
            # Not going to filter systems by status so able to link drafts, testing, etc
            self.fields['related_systems'].queryset = SystemModule.objects.all()
        except ImportError:
            # If projects app not available, hide field
            self.fields['related_systems'].widget = forms.HiddenInput()
    
    def clean_slug(self):
        """Auto-generate slug from degree and institution."""
        slug = self.cleaned_data.get('slug')
        degree = self.cleaned_data.get('degree')
        institution = self.cleaned_data.get('institution')

        if not slug and degree and institution:
            slug = slugify(f"{degree} {institution}")
        
        # Check for uniqueness
        if slug:
            existing = Education.objects.filter(slug=slug)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError(
                    f"An education entry with slug '{slug}' already exists."
                )

        return slug
    
    def clean_end_date(self):
        """Validate end date logic."""
        start_date = self.cleaned_data.get("start_date")
        end_date = self.cleaned_data.get("end_date")
        is_current = self.cleaned_data.get("is_current")

        if is_current and end_date:
            raise ValidationError("Current education should not have an end date.")

        if not is_current and not end_date:
            raise ValidationError("Completed education must have an end date.")

        if start_date and end_date and end_date < start_date:
            raise ValidationError("End date cannot be before start date.")

        if end_date and end_date > date.today():
            raise ValidationError("End date cannot be in the future.")

        return end_date


class EducationSkillDevelopmentForm(forms.ModelForm):
    """Form for managing Education-Skill development connections."""

    class Meta:
        model = EducationSkillDevelopment
        fields = [
            "education",
            "skill",
            "proficiency_before",
            "proficiency_after",
            "learning_focus",
            "importance_in_curriculum",
            "learning_notes",
        ]
        widgets = {
            "education": forms.Select(attrs={"class": "form-control"}),
            "skill": forms.Select(attrs={"class": "form-control"}),
            "proficiency_before": forms.Select(attrs={"class": "form-control"}),
            "proficiency_after": forms.Select(attrs={"class": "form-control"}),
            "learning_focus": forms.Select(attrs={"class": "form-control"}),
            "importance_in_curriculum": forms.Select(attrs={"class": "form-control"}),
            "learning_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Specific learning outcomes or projects...",
                }
            ),
        }
    
    def clean(self):
        """Cross-field validation for proficiency progression."""
        cleaned_data = super().clean()
        proficiency_before = cleaned_data.get("proficiency_before")
        proficiency_after = cleaned_data.get("proficiency_after")

        if proficiency_before is not None and proficiency_after is not None:
            if proficiency_after <= proficiency_before:
                raise ValidationError(
                    f"Proficiency after must be higher than proficiency before ({proficiency_before}). "
                    "Learning should result in skill improvement."
                )

        return cleaned_data


class ExperienceForm(forms.ModelForm):
    """Enhanced experience form with technology tracking."""

    class Meta:
        model = Experience
        fields = [
            "company",
            "slug",
            "position",
            "location",
            "description",
            "start_date",
            "end_date",
            "is_current",
            "technologies",
        ]
        widgets = {
            "company": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Company Name"}
            ),
            "slug": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "auto-generated-from-position-company",
                }
            ),
            "position": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Job Title/Position"}
            ),
            "location": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "City, State or Remote"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Describe your role, responsibilities, and achievements...",
                }
            ),
            "start_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "end_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "is_current": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "technologies": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Python, Django, React, AWS (comma-separated)",
                }
            ),
        }
    
    def clean_slug(self):
        """Auto-generate slug from position and company."""
        slug = self.cleaned_data.get("slug")
        position = self.cleaned_data.get("position")
        company = self.cleaned_data.get("company")

        if not slug and position and company:
            slug = slugify(f"{position} {company}")

        # Check for uniqueness
        if slug:
            existing = Experience.objects.filter(slug=slug)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError(
                    f"An experience with slug '{slug}' already exists."
                )

        return slug

    def clean_end_date(self):
        """Validate end date logic."""
        start_date = self.cleaned_data.get("start_date")
        end_date = self.cleaned_data.get("end_date")
        is_current = self.cleaned_data.get("is_current")

        if is_current and end_date:
            raise ValidationError("Current positions should not have an end date.")

        if not is_current and not end_date:
            raise ValidationError("Non-current positions must have an end date.")

        if start_date and end_date and end_date < start_date:
            raise ValidationError("End date cannot be before start date.")

        if end_date and end_date > date.today():
            raise ValidationError("End date cannot be in the future.")

        return end_date


class ContactForm(forms.ModelForm):
    """Enhanced contact form with all tracking fields."""

    class Meta:
        model = Contact
        fields = [
            "name",
            "email",
            "subject",
            "message",
            "is_read",
            "referrer_page",
            "user_agent",
            "ip_address",
            "response_sent",
            "response_date",
            "inquiry_category",
            "priority",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Contact Name"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "email@example.com"}
            ),
            "subject": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Inquiry Subject"}
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Contact message...",
                }
            ),
            "is_read": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "referrer_page": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Page visitor came from"}
            ),
            "user_agent": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Browser/device info",
                }
            ),
            "ip_address": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "192.168.1.1"}
            ),
            "response_sent": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "response_date": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
            "inquiry_category": forms.Select(attrs={"class": "form-control"}),
            "priority": forms.Select(attrs={"class": "form-control"}),
        }
    
    def clean_response_date(self):
        """Validate response date logic."""
        response_sent = self.cleaned_data.get("response_sent")
        response_date = self.cleaned_data.get("response_date")

        if response_sent and not response_date:
            raise ValidationError(
                "Response date is required when response is marked as sent."
            )

        if response_date and response_date > timezone.now():
            raise ValidationError("Response date cannot be in the future.")

        return response_date


class SocialLinkForm(forms.ModelForm):
    """Form for managing social media links."""

    class Meta:
        model = SocialLink
        fields = ["name", "url", "handle", "icon", "display_order"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Platform Name (e.g., GitHub, LinkedIn)",
                }
            ),
            "url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://github.com/yourusername",
                }
            ),
            "handle": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "@username or handle"}
            ),
            "icon": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "fa-github (FontAwesome icon name)",
                }
            ),
            "display_order": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
        }

    def clean_url(self):
        """Validate URL format."""
        url = self.cleaned_data.get("url")
        if url and not url.startswith(("http://", "https://")):
            url = "https://" + url
        return url


class PortfolioAnalyticsForm(forms.ModelForm):
    """Enhanced portfolio analytics form with comprehensive metrics."""
    # TODO: Enhance logic for replacing static values w generated analytics

    class Meta:
        model = PortfolioAnalytics
        fields = [
            "date",
            "learning_hours_logged",
            "datalog_entries_written",
            "skills_practiced",
            "projects_worked_on",
            "milestones_achieved",
            "unique_visitors",
            "page_views",
            "datalog_views",
            "system_views",
            "contact_form_submissions",
            "github_clicks",
            "resume_downloads",
            "top_datalog",
            "top_system",
            "top_country",
            "top_city",
            "top_referrer",
            "job_board_visits",
            "bounce_rate",
            "avg_session_duration",
            "organic_search_percentage",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "learning_hours_logged": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "max": 24,
                    "step": 0.5,
                    "placeholder": "Hours spent learning/coding",
                }
            ),
            "datalog_entries_written": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "placeholder": "Learning entries written",
                }
            ),
            "skills_practiced": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "placeholder": "Number of skills practiced",
                }
            ),
            "projects_worked_on": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "placeholder": "Projects worked on",
                }
            ),
            "milestones_achieved": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "placeholder": "Learning milestones reached",
                }
            ),
            "unique_visitors": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "placeholder": "Unique visitors",
                }
            ),
            "page_views": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "placeholder": "Total page views",
                }
            ),
            "datalog_views": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "placeholder": "DataLog views",
                }
            ),
            "system_views": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "placeholder": "System views"}
            ),
            "contact_form_submissions": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "placeholder": "Contact submissions",
                }
            ),
            "github_clicks": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "placeholder": "GitHub profile clicks",
                }
            ),
            "resume_downloads": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "placeholder": "Resume downloads",
                }
            ),
            "top_datalog": forms.Select(attrs={"class": "form-control"}),
            "top_system": forms.Select(attrs={"class": "form-control"}),
            "top_country": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Top visitor country"}
            ),
            "top_city": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Top visitor city"}
            ),
            "top_referrer": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Top referrer website"}
            ),
            "job_board_visits": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "placeholder": "Visits from job boards",
                }
            ),
            "bounce_rate": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "max": 100,
                    "step": 0.1,
                    "placeholder": "Bounce rate percentage",
                }
            ),
            "avg_session_duration": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "placeholder": "Average session duration (seconds)",
                }
            ),
            "organic_search_percentage": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "max": 100,
                    "step": 0.1,
                    "placeholder": "Organic search percentage",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate foreign key choices
        try:
            from blog.models import Post
            from projects.models import SystemModule

            self.fields["top_datalog"].queryset = Post.objects.filter(
                status="published"
            )
            self.fields["top_datalog"].empty_label = "Select top DataLog..."

            self.fields["top_system"].queryset = SystemModule.objects.filter(
                status__in=["deployed", "published"]
            )
            self.fields["top_system"].empty_label = "Select top System..."
        except ImportError:
            pass

    def clean_date(self):
        """Validate date is not in the future and not duplicate."""
        date_value = self.cleaned_data.get("date")

        if date_value and date_value > date.today():
            raise ValidationError("Analytics date cannot be in the future.")

        # Check for duplicate dates
        if date_value:
            existing = PortfolioAnalytics.objects.filter(date=date_value)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError(f"Analytics for {date_value} already exist.")

        return date_value

    def clean_learning_hours_logged(self):
        """Validate learning hours is reasonable."""
        hours = self.cleaned_data.get("learning_hours_logged")
        if hours and hours > 16:  # Max 16 hours of learning per day
            raise ValidationError("Learning hours per day seems unusually high.")
        return hours

    def clean_page_views(self):
        """Validate page views is reasonable compared to visitors."""
        page_views = self.cleaned_data.get("page_views")
        unique_visitors = self.cleaned_data.get("unique_visitors")

        if page_views and unique_visitors:
            if page_views < unique_visitors:
                raise ValidationError("Page views cannot be less than unique visitors.")

            # Warn if page views per visitor is unusually high
            if page_views > unique_visitors * 50:
                raise ValidationError(
                    f"Page views per visitor ({page_views / unique_visitors:.1f}) seems unusually high. "
                    "Please verify the data."
                )

        return page_views

    def clean_bounce_rate(self):
        """Validate bounce rate is a percentage."""
        bounce_rate = self.cleaned_data.get("bounce_rate")
        if bounce_rate and (bounce_rate < 0 or bounce_rate > 100):
            raise ValidationError("Bounce rate must be between 0 and 100.")
        return bounce_rate

    def clean_organic_search_percentage(self):
        """Validate organic search percentage."""
        percentage = self.cleaned_data.get("organic_search_percentage")
        if percentage and (percentage < 0 or percentage > 100):
            raise ValidationError(
                "Organic search percentage must be between 0 and 100."
            )
        return percentage
