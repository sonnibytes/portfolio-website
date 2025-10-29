"""
Projects Admin Forms for Systems Management
Enhanced forms with AURA styling and validation
Version 2.0
"""

from django import forms
from django.utils.text import slugify
from markdownx.fields import MarkdownxFormField
from .models import SystemModule, Technology, SystemType, ArchitectureComponent, ArchitectureConnection, SystemSkillGain
from core.models import Skill


# NEW: For new skill-tech relationship

class SystemSkillGainForm(forms.ModelForm):
    """Enhanced form for managing system skill gains with technology connections."""
    
    class Meta:
        model = SystemSkillGain
        fields = [
            'system',
            'skill', 
            'proficiency_gained',
            'technologies_used',
            'how_learned',
        ]
        widgets = {
            'system': forms.Select(attrs={
                'class': 'w-full px-3 py-2 bg-black bg-opacity-30 border border-gray-600 rounded-lg text-white focus:border-teal-400 focus:outline-none',
            }),
            'skill': forms.Select(attrs={
                'class': 'w-full px-3 py-2 bg-black bg-opacity-30 border border-gray-600 rounded-lg text-white focus:border-teal-400 focus:outline-none',
            }),
            'proficiency_gained': forms.Select(attrs={
                'class': 'w-full px-3 py-2 bg-black bg-opacity-30 border border-gray-600 rounded-lg text-white focus:border-teal-400 focus:outline-none',
            }),
            'technologies_used': forms.CheckboxSelectMultiple(attrs={
                'class': 'technology-checkboxes space-y-2'
            }),
            'how_learned': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 bg-black bg-opacity-30 border border-gray-600 rounded-lg text-white focus:border-teal-400 focus:outline-none',
                'placeholder': 'Tutorial, documentation, experimentation, etc.'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Order querysets for better UX
        self.fields['system'].queryset = SystemModule.objects.order_by('title')
        self.fields['skill'].queryset = Skill.objects.order_by('category', 'name')
        self.fields['technologies_used'].queryset = Technology.objects.order_by('category', 'name')
        
        # Make some fields optional
        self.fields['how_learned'].required = False
        
        # Add help text
        self.fields['proficiency_gained'].help_text = "What level of proficiency did you gain with this skill from this project?"
        self.fields['technologies_used'].help_text = "Which technologies were used to apply this skill in this project?"
    
    # def clean_time_invested_hours(self):
    #     """Validate time invested hours"""
    #     hours = self.cleaned_data.get('time_invested_hours')
    #     if hours is not None and hours < 0:
    #         raise forms.ValidationError("Time invested cannot be negative.")
    #     return hours


class SystemModuleForm(forms.ModelForm):
    """Enhanced form for creating and editing systems."""
    
    description = MarkdownxFormField(
        help_text="Full system description in Markdown format",
        widget=forms.Textarea(attrs={
            'rows': 15,
            'class': 'markdownx-editor form-control',
            'placeholder': 'Describe your system, its purpose, features, and implementation...'
        })
    )
    
    usage_examples = MarkdownxFormField(
        help_text="Usage examples and key features",
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 8,
            'class': 'markdownx-editor form-control',
            'placeholder': 'Provide usage examples...'
        })
    )
    
    setup_instructions = MarkdownxFormField(
        help_text="Setup instructions and implementation details",
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 10,
            'class': 'markdownx-editor form-control',
            'placeholder': 'List setup instructions...'
        })
    )
    
    challenges = MarkdownxFormField(
        help_text="Development challenges and solutions",
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 8,
            'class': 'markdownx-editor form-control',
            'placeholder': 'Challenges faced and how they were overcome...'
        })
    )
    
    # future_enhancements = MarkdownxFormField(
    #     help_text="Planned improvements and next steps",
    #     required=False,
    #     widget=forms.Textarea(attrs={
    #         'rows': 6,
    #         'class': 'markdownx-editor form-control',
    #         'placeholder': 'Future improvements and planned features...'
    #     })
    # )
    
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
            'description', 'usage_examples', 'setup_instructions', 'challenges', 
            'system_type', 'technologies', 'complexity', 'priority',
            'status', 'featured', 'completion_percent',
            'performance_score', 'uptime_percentage', 'response_time_ms', 'daily_users',
            'github_url', 'live_url', 'demo_url', 'documentation_url',
            'thumbnail', 'banner_image', 'featured_image', 
            'estimated_dev_hours', 'actual_dev_hours', 'team_size'
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
            'response_time_ms': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'daily_users': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
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
            # 'architecture_diagram': forms.FileInput(attrs={
            #     'class': 'form-control',
            #     'accept': 'image/*'
            # }),
            'estimated_dev_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'actual_dev_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'team_size': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'value': 1
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
            'response_time_ms': 'Average response time in milliseconds',
            'daily_users': 'Average daily active users',
            'thumbnail': 'System card thumbnail (400x300px recommended)',
            'banner_image': 'Header banner image (1200x400px recommended)',
            'featured_image': 'Featured image for homepage (800x600px recommended)',
            # 'architecture_diagram': 'System architecture diagram',
            'estimated_dev_hours': 'Estimated development hours',
            'actual_dev_hours': 'Actual development hours spent',
            'team_size': 'Number of team members',
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
            self.fields['team_size'].initial = 1

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
        
        # Validate development hours
        estimated = cleaned_data.get('estimated_dev_hours')
        actual = cleaned_data.get('actual_dev_hours')
        if estimated is not None and estimated < 0:
            raise forms.ValidationError('Estimated development hours cannot be negative.')
        if actual is not None and actual < 0:
            raise forms.ValidationError('Actual development hours cannot be negative.')
        
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


# ============================================================================
# ARCHITECTURE COMPONENT FORM
# ============================================================================

class ArchitectureComponentForm(forms.ModelForm):
    """Enhanced form for architecture components with AURA styling"""
    
    class Meta:
        model = ArchitectureComponent
        fields = [
            'system', 'name', 'component_type', 'description', 'technology',
            'position_x', 'position_y', 'position_z',
            'color', 'size', 'is_core', 'display_order'
        ]
        widgets = {
            'system': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'Select system...'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Streamlit Frontend, API Gateway...'
            }),
            'component_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe the component\'s role and functionality...'
            }),
            'technology': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'Select primary technology (optional)...'
            }),
            'position_x': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5',
                'min': '-5',
                'max': '5',
                'placeholder': '0.0'
            }),
            'position_y': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.5',
                'min': '-5',
                'max': '5',
                'placeholder': '0.0'
            }),
            'position_z': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5', 
                'min': '-5',
                'max': '5',
                'placeholder': '0.0'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control color-picker',
                'type': 'color',
                'value': '#00ffff'
            }),
            'size': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '5',
                'max': '50',
                'placeholder': '15'
            }),
            'is_core': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'display_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set empty labels for better styling
        self.fields['system'].empty_label = 'Select System...'
        self.fields['technology'].empty_label = 'No specific technology'
        
        # Add help text
        self.fields['position_x'].help_text = 'X coordinate (-5 to +5, 0 = center)'
        self.fields['position_y'].help_text = 'Y coordinate (-5 to +5, 0 = center)'
        self.fields['position_z'].help_text = 'Z coordinate (-5 to +5, 0 = center)'
        self.fields['size'].help_text = 'Visual size in diagram (5-50, 15 recommended)'
        self.fields['is_core'].help_text = 'Mark as central/core component'
        self.fields['display_order'].help_text = 'Lower numbers appear first'
    
    def clean(self):
        cleaned_data = super().clean()

        # Validate position coords
        for coord in ['position_x', 'position_y', 'position_z']:
            value = cleaned_data.get(coord)
            if value is not None and (value < -5 or value > 5):
                self.add_error(coord, 'Position must be between -5 and +5')
        
        # Validate size
        size = cleaned_data.get('size')
        if size and (size < 5 or size > 50):
            self.add_error('size', 'Size must be between 5 and 50')
        
        # Validate color format
        color = cleaned_data.get('color')
        if color and not color.startswith('#'):
            cleaned_data['color'] = f'#{color}'
        
        return cleaned_data


# ============================================================================
# ARCHITECTURE CONNECTION FORM
# ============================================================================

class ArchitectureConnectionForm(forms.ModelForm):
    """Enhanced form for architecture connections"""
    
    class Meta:
        model = ArchitectureConnection
        fields = [
            'from_component', 'to_component', 'connection_type', 'label',
            'line_color', 'line_width', 'is_bidirectional'
        ]
        widgets = {
            'from_component': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'Select source component...'
            }),
            'to_component': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'Select target component...'
            }),
            'connection_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'label': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., API Request, Data Flow, Authentication...'
            }),
            'line_color': forms.TextInput(attrs={
                'class': 'form-control color-picker',
                'type': 'color',
                'value': '#00ffff'
            }),
            'line_width': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10',
                'value': '2'
            }),
            'is_bidirectional': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Group components by system for better UX
        components = ArchitectureComponent.objects.select_related('system').order_by(
            'system__title', 'name'
        )
        
        choices = [('', 'Select component...')]
        current_system = None
        
        for component in components:
            if current_system != component.system.title:
                if current_system is not None:
                    # Close previous optgroup (handled by Django)
                    pass
                current_system = component.system.title
                # Django will handle optgroup creation
            
            label = f"{component.system.title} → {component.name}"
            choices.append((component.pk, label))
        
        self.fields['from_component'].choices = choices
        self.fields['to_component'].choices = choices
        
        # Add help text
        self.fields['label'].help_text = 'Optional label for the connection line'
        self.fields['line_width'].help_text = 'Line thickness (1-10, 2 recommended)'
        self.fields['is_bidirectional'].help_text = 'Two-way connection (arrows on both ends)'
    
    def clean(self):
        cleaned_data = super().clean()
        from_component = cleaned_data.get('from_component')
        to_component = cleaned_data.get('to_component')
        
        # Prevent self-connections
        if from_component and to_component and from_component == to_component:
            raise forms.ValidationError('A component cannot connect to itself.')
        
        # Check for duplicate connections
        if from_component and to_component:
            existing = ArchitectureConnection.objects.filter(
                from_component=from_component,
                to_component=to_component
            )
            
            # Exclude current instance when editing
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise forms.ValidationError(
                    'A connection between these components already exists.'
                )
        
        # Validate line width
        line_width = cleaned_data.get('line_width')
        if line_width and (line_width < 1 or line_width > 10):
            self.add_error('line_width', 'Line width must be between 1 and 10')
        
        return cleaned_data


# ============================================================================
# BULK ARCHITECTURE CREATION FORM
# ============================================================================

class BulkArchitectureForm(forms.Form):
    """Form for creating default architecture for multiple systems"""
    
    systems = forms.ModelMultipleChoiceField(
        queryset=SystemModule.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        help_text='Select systems to create default architecture for'
    )
    
    architecture_type = forms.ChoiceField(
        choices=[
            ('auto', 'Auto-detect based on technologies'),
            ('web_app', 'Web Application'),
            ('api_service', 'API Service'),
            ('data_pipeline', 'Data Pipeline'),
            ('ml_project', 'Machine Learning Project'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        initial='auto',
        help_text='Type of architecture to create'
    )
    
    clear_existing = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Clear existing architecture components before creating new ones'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Only show systems without architecture by default
        systems_without_arch = SystemModule.objects.filter(
            architecture_components__isnull=True
        ).distinct()
        
        if systems_without_arch.exists():
            self.fields['systems'].queryset = systems_without_arch
            self.fields['systems'].help_text = 'Systems without existing architecture'
        else:
            self.fields['systems'].help_text = 'All systems (some already have architecture)'


# ============================================================================
# SYSTEM SELECTION WIDGET FOR BETTER UX
# ============================================================================

class SystemSelectWidget(forms.Select):
    """Custom widget for system selection with enhanced display"""
    
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        
        if value:
            try:
                system = SystemModule.objects.get(pk=value)
                option['attrs']['data-status'] = system.status
                option['attrs']['data-type'] = system.system_type.name if system.system_type else ''
                option['attrs']['data-components'] = system.architecture_components.count()
            except SystemModule.DoesNotExist:
                pass
        
        return option
