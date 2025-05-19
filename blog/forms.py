from django import forms
from django.utils.text import slugify
from markdownx.fields import MarkdownxFormField
from .models import Post, Category, Tag, Series, SeriesPost


class PostForm(forms.ModelForm):
    """Form for creating and editing posts/logs."""

    ######################### CONTENT FIELDS #########################

    # Use MarkdownxFormField for content with better widget
    content = MarkdownxFormField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control markdown-editor",
                "rows": 25,
                "placeholder": "Write your post content here using Markdown...",
            }
        )
    )
    
    # Category as a select field with empty option
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=True,
        empty_label="Select a Category",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    ######################### TAG FIELDS #########################

    # Tags as a multiple select field
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all().order_by('name'),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select tags-select',
            'size': '5'})
    )

    # Create a new tag field
    new_tags = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Add new tags (comma-separated)",
            }
        ),
    )

    ######################### SERIES FIELDS #########################

    # Series field
    series = forms.ModelChoiceField(
        queryset=Series.objects.all().order_by('title'),
        required=False,
        empty_label="Select a series (optional)",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    # Position in Series
    series_order = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Position in series'
        })
    )

    # Create a new series
    new_series = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create new series'
        })
    )

    ######################### PREVIEW TOGGLE #########################

    # Preview toggle for the form
    show_preview = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )



    # # Add a field for the intro section
    # introduction = forms.CharField(
    #     widget=forms.Textarea(attrs={'rows': 4}),
    #     help_text="Brief introduction to post (auto formatted as <p>)",
    #     required=False
    # )

    # # Fields for each main section (up to 5 sections)
    # section_1_title = forms.CharField(max_length=200, required=False)
    # section_1_content = forms.CharField(
    #     widget=forms.Textarea(attrs={'rows': 6}), required=False)

    # section_2_title = forms.CharField(max_length=200, required=False)
    # section_2_content = forms.CharField(
    #     widget=forms.Textarea(attrs={"rows": 6}), required=False)

    # section_3_title = forms.CharField(max_length=200, required=False)
    # section_3_content = forms.CharField(
    #     widget=forms.Textarea(attrs={"rows": 6}), required=False)

    # section_4_title = forms.CharField(max_length=200, required=False)
    # section_4_content = forms.CharField(
    #     widget=forms.Textarea(attrs={"rows": 6}), required=False)

    # section_5_title = forms.CharField(max_length=200, required=False)
    # section_5_content = forms.CharField(
    #     widget=forms.Textarea(attrs={"rows": 6}), required=False)

    # # Field for code snippet (with language selection)
    # code_snippet = forms.CharField(
    #     widget=forms.Textarea(attrs={'rows': 8, 'class': 'code-editor'}),
    #     required=False
    # )
    # code_language = forms.ChoiceField(
    #     choices=[
    #         ('python', 'Python'),
    #         ('javascript', 'JavaScript'),
    #         ('html', 'HTML'),
    #         ('css', 'CSS'),
    #         ('bash', 'Bash/Shell'),
    #         ('sql', 'SQL'),
    #         ('json', 'JSON'),
    #     ],
    #     required=False
    # )

    # # Field for conclusion
    # conclusion = forms.CharField(
    #     widget=forms.Textarea(attrs={'rows': 4}),
    #     help_text="Conclusion or summary of the post",
    #     required=False
    # )

    class Meta:
        model = Post
        fields = [
            "title",
            "excerpt",
            "category",
            "tags",
            "status",
            "thumbnail",
            "banner_image",
            "featured",
            "featured_code",
            "featured_code_format",
            "show_toc",
            "published_date"
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter log title'
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description for post cards and previews'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'published_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'featured_code': forms.Textarea(attrs={
                'class': 'form-control code editor',
                'rows': 8,
                'placeholder': 'Code to display in featured entry section'
            }),
            'featured_code_format': forms.Select(attrs={
                'class': 'form-select'
            }),
            'show_toc': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_new_tags(self):
        """Process new tags entered as comma-separated values."""
        new_tags_str = self.cleaned_data.get('new_tags', '')
        if not new_tags_str:
            return []

        # Split by comma and strip whitespace
        tag_names = [name.strip() for name in new_tags_str.split(',') if name.strip()]
        tags = []

        # Create new tags
        for name in tag_names:
            slug = slugify(name)
            tag, created = Tag.objects.get_or_create(
                slug=slug,
                defaults={'name': name}
            )
            tags.append(tag)

        return tags

    def clean_new_series(self):
        """Process new series entered."""

        new_series = self.cleaned_data.get('new_series', '')
        if not new_series:
            return None

        # Create new series
        slug = slugify(new_series)
        series, created = Series.objects.get_or_create(
            slug=slug,
            defaults={'title': new_series}
        )

        return series
    
    def clean(self):
        """Validate form data."""

        cleaned_data = super().clean()

        # Handle series logic
        series = cleaned_data.get('series')
        new_series = cleaned_data.get('new_series')
        series_order = cleaned_data.get('series_order')

        # If both series and new_series provided, use new_series
        if new_series:
            cleaned_data['series'] = new_series

        # Ensure order is provided if series is selected
        if (series or new_series) and not series_order:
            self.add_error('series_order', 'Order is required when adding to a series')

        return cleaned_data

    def save(self, commit=True):
        """
        Override save method to compile structured content from sections
        into a single markdown document with proper heading levels.
        """
        post = super().save(commit=False)

        if commit:
            post.save()

            # Handle tags
            self.cleaned_data['tags'] = list(self.cleaned_data.get('tags', []))
            new_tags = self.cleaned_data.get('new_tags', [])
            if new_tags:
                self.cleaned_data['tags'].extend(new_tags)
            self.save_m2m()

            # Handle series
            series = self.cleaned_data.get('series')
            series_order = self.cleaned_data.get('series_order')

            if series and series_order:
                # Delete existing series association if any
                SeriesPost.objects.filter(post=post).delete()

                # Create new series association
                SeriesPost.objects.create(
                    series=series,
                    post=post,
                    order=series_order
                )
        return post

        # # Start building the markdown content
        # markdown_content = []

        # # Add intro if provided
        # if self.cleaned_data.get('introduction'):
        #     markdown_content.append(self.cleaned_data['introduction'])
        #     markdown_content.append("\n")

        # # Add each section with proper markdown heading (##)
        # for i in range(1, 6):
        #     section_title = self.cleaned_data.get(f'section_{i}_title')
        #     section_content = self.cleaned_data.get(f'section_{i}_content')

        #     if section_title and section_content:
        #         markdown_content.append(f"## {section_title}")
        #         markdown_content.append("\n")
        #         markdown_content.append(section_content)
        #         markdown_content.append("\n")

        # # Add code snippet if provided
        # code_snippet = self.cleaned_data.get('code_snippet')
        # code_language = self.cleaned_data.get('code_language')

        # if code_snippet and code_language:
        #     markdown_content.append(f"```{code_language}")
        #     markdown_content.append(code_snippet)
        #     markdown_content.append("```")
        #     markdown_content.append("\n")

        # # Add conclusion if provided
        # if self.cleaned_data.get('conclusion'):
        #     markdown_content.append("## Conclusion")
        #     markdown_content.append("\n")
        #     markdown_content.append(self.cleaned_data["conclusion"])

        # # Join all content with a doube newlines for readability
        # post.content = "\n\n".join(markdown_content)

        # if commit:
        #     post.save()
        #     self.save_m2m()

        # return post

class CategoryForm(forms.ModelForm):
    """Form for creating and editing categories."""
    class Meta:
        model = Category
        fields = ['name', 'code', 'description', 'color', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': 2,
                'placeholder': 'Two-letter code'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control color-picker',
                'type': 'color',
                'value': '#00f0ff'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Font Awesome class (e.g., fa-code)'
            }),
        }


class TagForm(forms.ModelForm):
    """Form for creating and editing tags."""
    class Meta:
        model = Tag
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
        }


class SeriesForm(forms.ModelForm):
    """Form for creating and editing series."""
    class Meta:
        model = Series
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
