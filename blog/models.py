from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils import timezone
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
import re


class Category(models.Model):
    """Category model for oraganizing blog posts."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    code = models.CharField(max_length=2,
                            help_text="Two-letter code for display in hexagon")
    description = models.TextField(blank=True)
    color = models.CharField(
        max_length=7, default="#00f0ff",
        help_text="Hex color code (e.g., #00f0ff)")
    icon = models.CharField(
        max_length=50, blank=True,
        help_text="Font Awesome icon name (e.g., fa-book-open)")

    class Meta:
        verbose_name_plural = "categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:category', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=20)
    slug = models.SlugField(unique=True, max_length=50)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:tag', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Tag, self).save(*args, **kwargs)


class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    # Code format options
    CODE_FORMAT_CHOICES = (
        ("python", "Python"),
        ("javascript", "JavaScript"),
        ("html", "HTML"),
        ("css", "CSS"),
        ("terminal", "Terminal"),
        ("markdown", "Markdown"),
        ("json", "JSON"),
        ("sql", "SQL"),
        ("bash", "Bash/Shell"),
        ("plaintext", "Plain Text"),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    excerpt = models.TextField(
        blank=True, help_text="Short description for display in post cards")
    featured = models.BooleanField(
        default=False, help_text="Feature this post on the blog homepage")
    thumbnail = models.ImageField(
        upload_to="blog/thumbnails/", null=True, blank=True,
        help_text="Small image for post cards (300x200px recommended)")
    banner_image = models.ImageField(
        upload_to="blog/banners/", blank=True, null=True,
        help_text="Large banner img for post header (1200x400px recommended)")
    featured_code = models.TextField(
        blank=True, help_text="Code snippet to display in featured section")
    featured_code_format = models.CharField(
        max_length=20,
        choices=CODE_FORMAT_CHOICES,
        default='python',
        help_text="Programming language for syntac highlighting")
    show_toc = models.BooleanField(
        default=True, help_text="Show table of contents on post page")
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='draft')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(blank=True, null=True)
    reading_time = models.PositiveIntegerField(
        default=0, editable=False,
        help_text="Estimated reading time in minutes")
    content = MarkdownxField()
    # Relationship Fields
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts"
        )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True, related_name="posts"
        )
    tags = models.ManyToManyField(Tag, blank=True, related_name="posts")

    class Meta:
        ordering = ['-published_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == 'published' and not self.published_date:
            self.published_date == timezone.now()
        # Calculate reading time
        if self.content:
            # Avg reading speed: 200 words per minute
            word_count = len(re.findall(r'\w+', self.content))
            self.reading_time = max(1, round(word_count / 200))
        if not self.excerpt and self.content:
            self.excerpt = self.content[:200] + '...'
        super(Post, self).save(*args, **kwargs)

    def rendered_content(self):
        """Return the content field as HTML."""
        return markdownify(self.content)

    def get_code_filename(self):
        """Return suitable filename for featured codeblock based on content."""
        # Map category codes to appropriate filenames
        category_to_filename = {
            'LJ': 'learning_journey.py',    # Learning Journey
            'TD': 'deep_dive.py',           # Technical Deep Dive
            'PD': 'proj_doc.md',            # Project Documentation
            'CT': 'career_path.md',         # Career Transition
            'NS': 'neural_spark.txt',       # Neural Sparks
            # Add technical category codes for spcific languages/technologies
            'PY': 'python_example.py',      # Python
            'JS': 'javascript_example.js',  # JavaScript
            'ML': 'ml_model.py',            # Machine Learning
            'AI': 'ai_model.py',            # AI
            'DS': 'data_analysis.py',       # Data Science
        }

        # Default to the category code's filename if available
        if self.category.code in category_to_filename:
            return category_to_filename[self.category.code]

        # Fallback based on title
        title_lower = self.title.lower()
        if 'python' in title_lower:
            return 'python_example.py'
        elif 'javascript' in title_lower or 'js' in title_lower:
            return 'javascript_example.js'
        elif 'machine learning' in title_lower or 'ml' in title_lower:
            return 'ml_model.py'
        elif 'django' in title_lower:
            return 'django_example.py'
        # General fall back
        return 'code_snippet.txt'

    def get_icon_text(self):
        """Return text to display as icon if no image available."""
        # Mapping of category codes to custom display text
        category_to_icon = {
            "LJ": "📚",  # Learning Journey - book emoji
            "TD": "🔍",  # Technical Deep Dive - magnifying glass
            "PD": "📋",  # Project Documentation - clipboard
            "CT": "🚀",  # Career Transition - rocket
            "NS": "💡",  # Neural Sparks - light bulb
            # Technical categories can remain as text
            "PY": "PY",
            "JS": "JS",
            "ML": "ML",
            "AI": "AI",
            "DS": "DS",
        }

        # Return the mapped icon text or category code
        return category_to_icon.get(self.category.code, self.category.code)


class Comment(models.Model):
    """Model for blog post comments."""
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return f"Comment by {self.name} on {self.post}"


class PostView(models.Model):
    """Model to track post views for popularity metrics."""
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='views')
    ip_address = models.GenericIPAddressField()
    viewed_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_on']
        unique_together = ('post', 'ip_address')

    def __str__(self):
        return f"View on {self.post} from {self.ip_address}"


class Series(models.Model):
    """Model for creating blog post series."""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Series"
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:series', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Series, self).save(*args, **kwargs)


class SeriesPost(models.Model):
    """Model for associating posts with a series and ordering them."""
    series = models.ForeignKey(
        Series, on_delete=models.CASCADE, related_name='posts')
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='series_associations')
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ('series', 'post')

    def __str__(self):
        return f"{self.post} in {self.series} (#{self.order})"
