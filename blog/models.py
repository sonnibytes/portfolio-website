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
    color = models.CharField(max_length=7, default="#00f0ff", help_text="Hex color code (e.g., #00f0ff)")
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon name (e.g., fa-book-open)")

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
        ordering = ['-published']

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
        """Return a suitable filename for the featured code block based on content."""
        # Map category codes to appropriate filenames

    def get_icon_text(self):
        """Return text to display as icon if no image available."""
        category_code = self.category.code
        match category_code:
            case 'ML':
