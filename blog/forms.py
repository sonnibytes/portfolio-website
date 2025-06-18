from django import forms
from django.utils.text import slugify
from markdownx.fields import MarkdownxFormField
from markdownx.widgets import MarkdownxWidget
from .models import Post, Category, Tag, Series, SeriesPost


class PostForm(forms.ModelForm):
    """Enhanced form for creating and editing DataLog posts."""

    # ================= CONTENT FIELDS =================

    # Enhanced content field w markdown
    content = MarkdownxFormField(
        widget=MarkdownxWidget(
            attrs={
                "class": "form-control markdown-editor",
                "rows": 25,
                "placeholder": "Write your DataLog content using Markdown...",
            }
        )
    )

    featured_code = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control code-editor",
                "rows": 10,
                "placeholder": "Paste your featured code snippet here...",
            }
        ),
        required=False,
        help_text="Optional code snippet to highlight in this DataLog",
    )

    # Tags as a multiple select field
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all().order_by("name"),
        required=False,
        widget=forms.SelectMultiple(
            attrs={"class": "form-select tags-select", "size": "5"}
        ),
    )

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "tag-selector"}),
        required=False,
        help_text="Select relevant tags for this DataLog",
    )

    related_systems = forms.ModelMultipleChoiceField(
        queryset=None,  # Will be set in __init__
        widget=forms.CheckboxSelectMultiple(attrs={"class": "system-selector"}),
        required=False,
        help_text="Link this DataLog to relevant systems",
    )

    class Meta:
        model = Post
        fields = [
            "title",
            "slug",
            "content",
            "excerpt",
            "category",
            "tags",
            "featured_code",
            "featured_code_format",
            "status",
            "featured",
            "show_toc",
            "complexity_level",
            "reading_time",
            "related_systems",
            "thumbnail",
            "banner_image",
            "published_date",
            "",
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
            tag, created_at = Tag.objects.get_or_create(
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
        series, created_at = Series.objects.get_or_create(
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
        """Save the post and handle tags and series."""

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

        """
        Can you tell me why we include some fields but not others? Like for the PostForm, we aren't including any of the image fields and some models don't have forms at all, and some forms don't have all the model fields?
        """


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
