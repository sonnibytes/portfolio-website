# blog/forms.py
"""
Blog Admin Forms for DataLogs Management
Enhanced forms with AURA styling and validation
Version 2.0
"""

from django import forms
from django.utils.text import slugify
from markdownx.fields import MarkdownxFormField
from .models import Post, Category, Tag, Series


class PostForm(forms.ModelForm):
    """Enhanced form for creating and editing DataLog posts."""
    
    content = MarkdownxFormField(
        help_text="Write your DataLog content in Markdown format",
        widget=forms.Textarea(attrs={
            'rows': 20,
            'class': 'markdownx-editor',
            'placeholder': 'Enter your technical log content here...'
        })
    )
    
    excerpt = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Brief summary of this DataLog entry...'
        }),
        help_text="Brief description for DataLog previews",
        required=False
    )
    
    featured_code = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 10,
            'class': 'form-control',
            'placeholder': 'Add featured code snippet here...'
        }),
        help_text="Code snippet to highlight in the DataLog",
        required=False
    )
    
    # Explicitly define tags field with proper queryset
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'tag-checkboxes'
        }),
        required=False,
        help_text="Select relevant tags for this DataLog",
        label="Tags"
    )

    # Explicitly define category field to ensure it has choices
    category = forms.ModelChoiceField(
        queryset=Category.objects.all().order_by('name'),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text="Primary category for this DataLog",
        empty_label="Select a category..."
    )

    # Explicitly define status field w choices
    status = forms.ChoiceField(
        choices=Post.STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text="Publication status"
    )

    # Explicitly define featured_code_format with choices
    featured_code_format = forms.ChoiceField(
        choices=Post.CODE_FORMAT_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text="Language for syntax highlighting"
    )

    class Meta:
        model = Post
        fields = [
            'title', 'slug', 'excerpt', 'content', 'category', 
            'tags', 'featured', 'status', 'thumbnail', 'banner_image',
            'featured_code', 'featured_code_format', 'show_toc'
        ]
        # Note: 'author' is excluded and set programmatically in the view
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter DataLog title...',
                'maxlength': 200
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'auto-generated-from-title',
                'help_text': 'Leave blank to auto-generate from title'
            }),
            'featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'show_toc': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'thumbnail': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'banner_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        
        help_texts = {
            'title': 'Descriptive title for your DataLog entry',
            'slug': 'URL-friendly version of title (auto-generated if empty)',
            'featured': 'Mark as featured DataLog',
            'show_toc': 'Show table of contents',
            'thumbnail': 'DataLog card thumbnail (400x300px recommended)',
            'banner_image': 'Header banner image (1200x400px recommended)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make slug field optional for new posts
        if not self.instance.pk:
            self.fields['slug'].required = False
        
        # Ensure querysets are fresh (important for dynamic content)
        self.fields["category"].queryset = Category.objects.all().order_by("name")
        self.fields["tags"].queryset = Tag.objects.all().order_by("name")

        # Add empty label for category if creating new post
        if not self.instance.pk:
            self.fields["category"].empty_label = "Select a category..."
            
        # Add CSS classes to all fields
        for field_name, field in self.fields.items():
            if field_name not in ['tags', 'featured', 'show_toc']:
                if 'class' not in field.widget.attrs:
                    field.widget.attrs.update({'class': 'admin-form-field'})
        
        # Set default status for new posts
        if not self.instance.pk:
            self.fields['status'].initial = 'draft'

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        title = self.cleaned_data.get('title')
        
        # Auto-generate slug if not provided
        if not slug and title:
            slug = slugify(title)
        
        # Check for uniqueness
        if slug:
            existing = Post.objects.filter(slug=slug)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError('A DataLog with this slug already exists.')
        
        return slug

    def clean(self):
        cleaned_data = super().clean()
        
        # Validate featured code format if featured code is provided
        featured_code = cleaned_data.get('featured_code')
        featured_code_format = cleaned_data.get('featured_code_format')
        
        if featured_code and not featured_code_format:
            raise forms.ValidationError(
                'Please select a code format when providing featured code.'
            )
        
        return cleaned_data


class CategoryForm(forms.ModelForm):
    """Form for creating and editing DataLog categories."""
    
    class Meta:
        model = Category
        fields = ['name', 'slug', 'code', 'description', 'color', 'icon']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Category name...',
                'maxlength': 100
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'auto-generated-from-name'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'XX',
                'maxlength': 2,
                'style': 'text-transform: uppercase;'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Category description...'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'value': '#00f0ff'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'fa-folder (Font Awesome icon name)'
            }),
        }
        
        help_texts = {
            'name': 'Display name for the category',
            'slug': 'URL-friendly version (auto-generated if empty)',
            'code': 'Two-letter code for hexagon display',
            'description': 'Brief description of this category',
            'color': 'Hex color code for theming',
            'icon': 'Font Awesome icon name (e.g., fa-code)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')
        
        if not slug and name:
            slug = slugify(name)
        
        if slug:
            existing = Category.objects.filter(slug=slug)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError('A category with this slug already exists.')
        
        return slug


class TagForm(forms.ModelForm):
    """Form for creating and editing DataLog tags."""
    
    class Meta:
        model = Tag
        fields = ['name', 'slug']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tag name...',
                'maxlength': 20
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'auto-generated-from-name'
            }),
        }
        
        help_texts = {
            'name': 'Tag name (keep it short)',
            'slug': 'URL-friendly version (auto-generated if empty)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')
        
        if not slug and name:
            slug = slugify(name)
        
        if slug:
            existing = Tag.objects.filter(slug=slug)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError('A tag with this slug already exists.')
        
        return slug


class SeriesForm(forms.ModelForm):
    """Form for creating and editing DataLog series."""
    
    class Meta:
        model = Series
        fields = [
            'title', 'slug', 'description', 'thumbnail', 
            'difficulty_level', 'is_complete', 'is_featured'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Series title...',
                'maxlength': 200
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'auto-generated-from-title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Series description...'
            }),
            'difficulty_level': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_complete': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'thumbnail': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        
        help_texts = {
            'title': 'Title for the DataLog series',
            'slug': 'URL-friendly version (auto-generated if empty)',
            'description': 'Description of what this series covers',
            'difficulty_level': 'Target audience difficulty level',
            'is_complete': 'Is this series complete?',
            'is_featured': 'Feature this series',
            'thumbnail': 'Series thumbnail (400x300px recommended)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        title = self.cleaned_data.get('title')
        
        if not slug and title:
            slug = slugify(title)
        
        if slug:
            existing = Series.objects.filter(slug=slug)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError('A series with this slug already exists.')
        
        return slug


# Quick forms for inline editing
class QuickPostStatusForm(forms.ModelForm):
    """Quick form for changing post status."""
    
    class Meta:
        model = Post
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control form-control-sm'})
        }


class QuickCategoryForm(forms.ModelForm):
    """Quick form for basic category creation."""
    
    class Meta:
        model = Category
        fields = ['name', 'code', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Category name'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'XX',
                'maxlength': 2
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'type': 'color'
            }),
        }