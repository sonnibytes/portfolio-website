from django import forms
from .models import SystemModule, Technology, SystemType


class SystemModuleForm(forms.ModelForm):
    """Enhanced form for creating and editing system modules (projects)."""

    technologies = forms.ModelMultipleChoiceField(
        queryset=Technology.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'technology-selector'
        }),
        required=False,
        help_text="Select all technologies used in this system"
    )

    class Meta:
        model = SystemModule
        fields = [
            "title",
            "slug",
            "description",
            "system_type",
            "status",
            "priority",
            "complexity",
            "technologies",
            "tech_stack",
            "github_repo",
            "demo_url",
            "performance_score",
            "code_quality_score",
            "test_coverage",
            "documentation_score",
            "challenges",
            "learning_outcomes",
            "future_improvements",
            "is_featured",
            "show_on_homepage",
            "is_public",
            "include_in_portfolio",
            "deployment_status",
        ]