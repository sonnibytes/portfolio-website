"""
Projects Admin Forms for Systems Management
Enhanced forms with AURA styling and validation
Version 2.0
"""

from django import forms
from django.utils.text import slugify
from markdownx.fields import MarkdownxFormField
from .models import SystemModule, Technology, SystemType


class SystemModuleForm(forms.ModelForm):
    """Enhanced form for creating and editing systems."""
    
    description = MarkdownxFormField(
        help_text="Full system description in Markdown format",
        widget=forms.Textarea(attrs={
            'rows': 15,
            'class': 'markdownx-editor',
            'placeholder': 'Describe your system, its purpose, features, and implementation...'
        })
    )
    
    features_overview = MarkdownxFormField(
        help_text="Key features and capabilities overview",
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 8,
            'class': 'markdownx-editor',
            'placeholder': 'List the main features and capabilities...'
        })
    )
    
    technical_details = MarkdownxFormField(
        help_text="Technical implementation details",
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 10,
            'class': 'markdownx-editor',
            'placeholder': 'Technical architecture, frameworks, databases, APIs...'
        })
    )
    
    challenges = MarkdownxFormField(
        help_text="Development challenges and solutions",
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 8,
            'class': 'markdownx-editor',
            'placeholder': 'Challenges faced and how they were overcome...'
        })
    )
    
    technologies = forms.ModelMultipleChoiceField(
        queryset=Technology.objects.all().order_by('category', 'name'),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'technology-checkboxes'
        }),
        required=False,
        help_text="Select technologies used in this system"
    )

    class Meta:
        model = SystemModule
        fields = [
            'title', 'slug', 'system_id', 'subtitle', 'excerpt',
            'description', 'features_overview', 'technical_details', 'challenges',
            'system_type', 'technologies', 'complexity', 'priority',
            'status', 'featured', 'completion_percent',
            'performance_score', 'uptime_percentage',
            'github_url', 'live_url', 'demo_url', 'documentation_url',
            'thumbnail', 'banner_image', 'featured_image'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter system title...',
                'maxlength': 200
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'auto-generated-from-title'
            }),
            'system_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SYS-001 (auto-generated if empty)'
            }),
            'subtitle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief subtitle or tagline...'
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief summary for system cards...'
            }),
            'system_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'complexity': forms.Select(attrs={
                'class': 'form-control'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'completion_percent': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100,
                'step': 0.1
            }),
            'performance_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100,
                'step': 0.1
            }),
            'uptime_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100,
                'step': 0.01
            }),
            'github_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/username/repo'
            }),
            'live_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://your-system.com'
            }),
            'demo_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://demo.your-system.com'
            }),
            'documentation_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://docs.your-system.com'
            }),
            'thumbnail': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'banner_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        
        help_texts = {
            'title': 'Descriptive title for your system',
            'slug': 'URL-friendly version of title (auto-generated if empty)',
            'system_id': 'Unique system identifier (auto-generated if empty)',
            'subtitle': 'Brief subtitle or tagline',
            'excerpt': 'Brief summary for system cards',
            'system_type': 'Category/type of this system',
            'complexity': 'Technical complexity level',
            'priority': 'Development/maintenance priority',
            'status': 'Current development status',
            'featured': 'Feature this system prominently',
            'completion_percent': 'Completion percentage (0-100)',
            'performance_score': 'Performance rating (0-100)',
            'uptime_percentage': 'Uptime percentage for deployed systems',
            'thumbnail': 'System card thumbnail (400x300px recommended)',
            'banner_image': 'Header banner image (1200x400px recommended)',
            'featured_image': 'Featured image for homepage (800x600px recommended)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make slug and system_id optional for new systems
        if not self.instance.pk:
            self.fields['slug'].required = False
            self.fields['system_id'].required = False
        
        # Ensure querysets are fresh
        self.fields['system_type'].queryset = SystemType.objects.all().order_by('name')
        self.fields['technologies'].queryset = Technology.objects.all().order_by('category', 'name')
        
        # Add empty labels
        if not self.instance.pk:
            self.fields['system_type'].empty_label = "Select a system type..."
        
        # Set default values for new systems
        if not self.instance.pk:
            self.fields['status'].initial = 'draft'
            self.fields['complexity'].initial = 2
            self.fields['priority'].initial = 2
            self.fields['completion_percent'].initial = 10

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        title = self.cleaned_data.get('title')
        
        if not slug and title:
            slug = slugify(title)
        
        if slug:
            existing = SystemModule.objects.filter(slug=slug)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError('A system with this slug already exists.')
        
        return slug

    def clean(self):
        cleaned_data = super().clean()
        
        # Validate performance metrics
        completion = cleaned_data.get('completion_percent')
        if completion is not None and (completion < 0 or completion > 100):
            raise forms.ValidationError('Completion percentage must be between 0 and 100.')
        
        performance = cleaned_data.get('performance_score')
        if performance is not None and (performance < 0 or performance > 100):
            raise forms.ValidationError('Performance score must be between 0 and 100.')
        
        uptime = cleaned_data.get('uptime_percentage')
        if uptime is not None and (uptime < 0 or uptime > 100):
            raise forms.ValidationError('Uptime percentage must be between 0 and 100.')
        
        return cleaned_data


class TechnologyForm(forms.ModelForm):
    """Form for creating and editing technologies."""
    
    class Meta:
        model = Technology
        fields = ['name', 'slug', 'description', 'category', 'icon', 'color']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Technology name...',
                'maxlength': 100
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'auto-generated-from-name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Technology description...'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'fa-python (Font Awesome icon name)'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'value': '#00f0ff'
            }),
        }
        
        help_texts = {
            'name': 'Technology or tool name',
            'slug': 'URL-friendly version (auto-generated if empty)',
            'description': 'Brief description of the technology',
            'category': 'Technology category',
            'icon': 'Font Awesome icon name (e.g., fa-python)',
            'color': 'Hex color code for theming',
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
            existing = Technology.objects.filter(slug=slug)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError('A technology with this slug already exists.')
        
        return slug


class SystemTypeForm(forms.ModelForm):
    """Form for creating and editing system types."""
    
    class Meta:
        model = SystemType
        fields = ['name', 'slug', 'code', 'description', 'color', 'icon', 'display_order']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'System type name...',
                'maxlength': 100
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'auto-generated-from-name'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'WEB',
                'maxlength': 4,
                'style': 'text-transform: uppercase;'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'System type description...'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'value': '#00f0ff'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'fa-globe (Font Awesome icon name)'
            }),
            'display_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
        }
        
        help_texts = {
            'name': 'Display name for the system type',
            'slug': 'URL-friendly version (auto-generated if empty)',
            'code': 'Short code for display (e.g., WEB, API, ML)',
            'description': 'Brief description of this system type',
            'color': 'Hex color code for theming',
            'icon': 'Font Awesome icon name (e.g., fa-globe)',
            'display_order': 'Display order (lower numbers appear first)',
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
            existing = SystemType.objects.filter(slug=slug)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError('A system type with this slug already exists.')
        
        return slug


# Quick forms for inline editing
class QuickSystemStatusForm(forms.ModelForm):
    """Quick form for changing system status."""
    
    class Meta:
        model = SystemModule
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control form-control-sm'})
        }


class QuickTechnologyForm(forms.ModelForm):
    """Quick form for basic technology creation."""
    
    class Meta:
        model = Technology
        fields = ['name', 'category', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Technology name'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control form-control-sm'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'type': 'color'
            }),
        }