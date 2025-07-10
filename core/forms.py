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
class ContactForm(forms.ModelForm):
    """Form for user contact submissions."""

    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        widget = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Message Subject'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Your message here...',
                'rows': 5
            }),
        }


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
