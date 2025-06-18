"""
Blog Forms - DataLogs Management
Minimal forms to get server running for testing
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from .models import Post, Category, Tag, Series


class PostForm(forms.ModelForm):
    """Form for creating and editing DataLog posts."""

    class Meta:
        model = Post
        fields = [
            "title",
            "slug",
            "excerpt",
            "content",
            "category",
            "tags",
            "featured",
            "status",
            "thumbnail",
            "banner_image",
            "featured_code",
            "featured_code_format",
            "show_toc",
        ]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": 20,
                    "class": "form-control content-editor",
                    "placeholder": "Write your DataLog content in Markdown...",
                }
            ),
            "excerpt": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "form-control",
                    "placeholder": "Brief description for post cards and search results...",
                }
            ),
            "title": forms.TextInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "placeholder": "Enter DataLog title...",
                }
            ),
            "slug": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "auto-generated-from-title",
                }
            ),
            "tags": forms.CheckboxSelectMultiple(),
            "category": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "featured_code_format": forms.Select(attrs={"class": "form-select"}),
            "featured_code": forms.Textarea(
                attrs={
                    "rows": 8,
                    "class": "form-control code-editor",
                    "placeholder": "Enter code snippet to highlight...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make certain fields optional in the form
        self.fields["slug"].required = False
        self.fields["excerpt"].required = False
        self.fields["featured_code"].required = False
        self.fields["thumbnail"].required = False
        self.fields["banner_image"].required = False

        # Add help text
        self.fields["slug"].help_text = "Leave blank to auto-generate from title"
        self.fields[
            "featured_code"
        ].help_text = "Code snippet to display in featured section"
        self.fields["content"].help_text = "Use Markdown formatting"

    def clean_slug(self):
        """Auto-generate slug if not provided."""
        slug = self.cleaned_data.get("slug")
        title = self.cleaned_data.get("title")

        if not slug and title:
            slug = slugify(title)

        # Check for uniqueness
        if slug:
            qs = Post.objects.filter(slug=slug)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(f"A post with slug '{slug}' already exists.")

        return slug

    def clean_title(self):
        """Validate title."""
        title = self.cleaned_data.get("title")
        if len(title) < 5:
            raise ValidationError("Title must be at least 5 characters long.")
        return title


class CategoryForm(forms.ModelForm):
    """Form for creating and editing categories."""

    class Meta:
        model = Category
        fields = ["name", "slug", "description", "color", "icon"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Category name..."}
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
                    "placeholder": "Brief description of this category...",
                }
            ),
            "color": forms.TextInput(
                attrs={
                    "type": "color",
                    "class": "form-control form-control-color",
                    "title": "Choose category color",
                }
            ),
            "icon": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "fas fa-folder",
                    "data-toggle": "tooltip",
                    "title": "FontAwesome icon class",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
        self.fields["description"].required = False
        self.fields["color"].initial = "#a855f7"  # Default lavender
        self.fields["icon"].initial = "fas fa-folder"

    def clean_slug(self):
        """Auto-generate slug if not provided."""
        slug = self.cleaned_data.get("slug")
        name = self.cleaned_data.get("name")

        if not slug and name:
            slug = slugify(name)

        return slug


class TagForm(forms.ModelForm):
    """Form for creating and editing tags."""

    class Meta:
        model = Tag
        fields = ["name", "slug"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Tag name..."}
            ),
            "slug": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "auto-generated-from-name",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False

    def clean_slug(self):
        """Auto-generate slug if not provided."""
        slug = self.cleaned_data.get("slug")
        name = self.cleaned_data.get("name")

        if not slug and name:
            slug = slugify(name)

        return slug


class SeriesForm(forms.ModelForm):
    """Form for creating and editing series."""

    class Meta:
        model = Series
        fields = ["title", "slug", "description", "is_complete", "is_featured"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Series title..."}
            ),
            "slug": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "auto-generated-from-title",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                    "placeholder": "Series description and overview...",
                }
            ),
            "is_complete": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_featured": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
        self.fields["description"].required = False

    def clean_slug(self):
        """Auto-generate slug if not provided."""
        slug = self.cleaned_data.get("slug")
        title = self.cleaned_data.get("title")

        if not slug and title:
            slug = slugify(title)

        return slug
