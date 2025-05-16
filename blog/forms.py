from django import forms
from markdownx.fields import MarkdownxFormField
from .models import Post, Category, Tag


class PostForm(forms.ModelForm):
    """Custom form for blog posts with better markdown structure."""

    # Use MarkdownxFormField for content with better widget
    content = MarkdownxFormField()

    # Add a field for the intro section
    introduction = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        help_text="Brief introduction to post (auto formatted as <p>)",
        required=False
    )

    # Fields for each main section (up to 5 sections)
    section_1_title = forms.CharField(max_length=200, required=False)
    section_1_content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6}), required=False)

    section_2_title = forms.CharField(max_length=200, required=False)
    section_2_content = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 6}), required=False)

    section_3_title = forms.CharField(max_length=200, required=False)
    section_3_content = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 6}), required=False)

    section_4_title = forms.CharField(max_length=200, required=False)
    section_4_content = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 6}), required=False)

    section_5_title = forms.CharField(max_length=200, required=False)
    section_5_content = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 6}), required=False)

    # Field for code snippet (with language selection)
    code_snippet = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 8, 'class': 'code-editor'}),
        required=False
    )
    code_language = forms.ChoiceField(
        choices=[
            ('python', 'Python'),
            ('javascript', 'JavaScript'),
            ('html', 'HTML'),
            ('css', 'CSS'),
            ('bash', 'Bash/Shell'),
            ('sql', 'SQL'),
            ('json', 'JSON'),
        ],
        required=False
    )

    # Field for conclusion
    conclusion = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        help_text="Conclusion or summary of the post",
        required=False
    )

    class Meta:
        model = Post
        fields = [
            'title', 'excerpt', 'category', 'tags', 'status',
            'thumbnail', 'banner_image', 'featured',
            'featured_code', 'featured_code_format', 'show_toc'
        ]
        widgets = {
            'excerpt': forms.Textarea(attrs={'rows': 3}),
            'featured_code': forms.Textarea(attrs={'rows': 6}),
        }

    def save(self, commit=True):
        """
        Override save method to compile structured content from sections
        into a single markdown document with proper heading levels.
        """
        post = super().save(commit=False)

        # Start building the markdown content
        markdown_content = []

        # Add intro if provided
        if self.cleaned_data.get('introduction'):
            markdown_content.append(self.cleaned_data['introduction'])
            markdown_content.append("\n")

        # Add each section with proper markdown heading (##)
        for i in range(1, 6):
            section_title = self.cleaned_data.get(f'section_{i}_title')
            section_content = self.cleaned_data.get(f'section_{i}_content')

            if section_title and section_content:
                markdown_content.append(f"## {section_title}")
                markdown_content.append("\n")
                markdown_content.append(section_content)
                markdown_content.append("\n")

        # Add code snippet if provided
        code_snippet = self.cleaned_data.get('code_snippet')
        code_language = self.cleaned_data.get('code_language')

        if code_snippet and code_language:
            markdown_content.append(f"```{code_language}")
            markdown_content.append(code_snippet)
            markdown_content.append("```")
            markdown_content.append("\n")

        # Add conclusion if provided
        if self.cleaned_data.get('conclusion'):
            markdown_content.append("## Conclusion")
            markdown_content.append("\n")
            markdown_content.append(self.cleaned_data["conclusion"])

        # Join all content with a doube newlines for readability
        post.content = "\n\n".join(markdown_content)

        if commit:
            post.save()
            self.save_m2m()

        return post
