# projects/forms.py
"""
Projects Forms - Systems Management
Minimal forms to get server running for testing
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from .models import SystemModule, Technology, SystemType


class SystemModuleForm(forms.ModelForm):
    """Form for creating and editing systems."""

    class Meta:
        model = SystemModule
        fields = [
            "name",
            "slug",
            "description",
            "system_type",
            "technologies",
            "status",
            "priority",
            "featured",
            "repository_url",
            "live_url",
            "completion_percent",
            "performance_score",
            "uptime_percentage",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "System name...",
                }
            ),
            "slug": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "auto-generated-from-name",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                    "placeholder": "System description and overview...",
                }
            ),
            "system_type": forms.Select(attrs={"class": "form-select"}),
            "technologies": forms.CheckboxSelectMultiple(),
            "status": forms.Select(attrs={"class": "form-select"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "repository_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://github.com/username/repo",
                }
            ),
            "live_url": forms.URLInput(
                attrs={"class": "form-control", "placeholder": "https://example.com"}
            ),
            "completion_percent": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "max": 100, "step": 1}
            ),
            "performance_score": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "max": 100, "step": 0.1}
            ),
            "uptime_percentage": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "max": 100, "step": 0.01}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make certain fields optional
        self.fields["slug"].required = False
        self.fields["repository_url"].required = False
        self.fields["live_url"].required = False
        self.fields["performance_score"].required = False
        self.fields["uptime_percentage"].required = False

        # Set initial values
        self.fields["completion_percent"].initial = 0
        self.fields["priority"].initial = 2  # Medium priority
        self.fields["status"].initial = "in_development"

        # Add help text
        self.fields["slug"].help_text = "Leave blank to auto-generate from name"
        self.fields[
            "completion_percent"
        ].help_text = "Overall completion percentage (0-100)"
        self.fields["performance_score"].help_text = "System performance score (0-100)"
        self.fields["uptime_percentage"].help_text = "System uptime percentage (0-100)"

    def clean_slug(self):
        """Auto-generate slug if not provided."""
        slug = self.cleaned_data.get("slug")
        name = self.cleaned_data.get("name")

        if not slug and name:
            slug = slugify(name)

        # Check for uniqueness
        if slug:
            qs = SystemModule.objects.filter(slug=slug)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(f"A system with slug '{slug}' already exists.")

        return slug

    def clean_name(self):
        """Validate system name."""
        name = self.cleaned_data.get("name")
        if len(name) < 3:
            raise ValidationError("System name must be at least 3 characters long.")
        return name

    def clean_completion_percent(self):
        """Validate completion percentage."""
        completion = self.cleaned_data.get("completion_percent")
        if completion is not None and (completion < 0 or completion > 100):
            raise ValidationError("Completion percentage must be between 0 and 100.")
        return completion

    def clean_performance_score(self):
        """Validate performance score."""
        score = self.cleaned_data.get("performance_score")
        if score is not None and (score < 0 or score > 100):
            raise ValidationError("Performance score must be between 0 and 100.")
        return score

    def clean_uptime_percentage(self):
        """Validate uptime percentage."""
        uptime = self.cleaned_data.get("uptime_percentage")
        if uptime is not None and (uptime < 0 or uptime > 100):
            raise ValidationError("Uptime percentage must be between 0 and 100.")
        return uptime


class TechnologyForm(forms.ModelForm):
    """Form for creating and editing technologies."""

    class Meta:
        model = Technology
        fields = ["name", "slug", "category", "description", "documentation_url"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Technology name..."}
            ),
            "slug": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "auto-generated-from-name",
                }
            ),
            "category": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "form-control",
                    "placeholder": "Technology description...",
                }
            ),
            "documentation_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://docs.example.com",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
        self.fields["description"].required = False
        self.fields["documentation_url"].required = False

    def clean_slug(self):
        """Auto-generate slug if not provided."""
        slug = self.cleaned_data.get("slug")
        name = self.cleaned_data.get("name")

        if not slug and name:
            slug = slugify(name)

        return slug


class SystemTypeForm(forms.ModelForm):
    """Form for creating and editing system types."""

    class Meta:
        model = SystemType
        fields = ["name", "slug", "description", "icon_class", "color_hex"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "System type name..."}
            ),
            "slug": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "auto-generated-from-name",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "form-control",
                    "placeholder": "System type description...",
                }
            ),
            "icon_class": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "fas fa-server",
                    "data-toggle": "tooltip",
                    "title": "FontAwesome icon class",
                }
            ),
            "color_hex": forms.TextInput(
                attrs={
                    "type": "color",
                    "class": "form-control form-control-color",
                    "title": "Choose type color",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
        self.fields["description"].required = False
        self.fields["color_hex"].initial = "#06b6d4"  # Default cyan
        self.fields["icon_class"].initial = "fas fa-server"

    def clean_slug(self):
        """Auto-generate slug if not provided."""
        slug = self.cleaned_data.get("slug")
        name = self.cleaned_data.get("name")

        if not slug and name:
            slug = slugify(name)

        return slug
