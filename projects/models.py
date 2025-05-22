from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
import re
from bs4 import BeautifulSoup

"""
NOTES ON VERBIAGE:
Systems > Projects
System Module > Individual Project
"""


class Technology(models.Model):
    """Tech model for categorizing project technologies."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Font Awesome icon name (e.g., fa-python)"
    )
    color = models.CharField(
        max_length=7,
        default="#00f0ff",
        help_text="Hex color code (e.g., #00f0ff)"
    )

    class Meta:
        verbose_name_plural = "technologies"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class SystemType(models.Model):
    """System Type model for categorizing projects/systems."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    code = models.CharField(max_length=3,
                            help_text="Short code for display in hexagon (e.g., ML, WEB)")
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7,
                             default="#00f0ff",
                             help_text="Hex color code for display accent (e.g., #00f0ff)")
    icon = models.CharField(
        max_length=50, blank=True,
        help_text="Font Awesome icon name (e.g. fa-robot)"
    )

    class Meta:
        verbose_name_plural = "system types"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("projects:system_type", args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class SystemModule(models.Model):
    """System Module model (Project model)."""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    COMPLEXITY_CHOICES = (
        (1, 'Basic'),
        (2, 'Intermediate'),
        (3, 'Advanced'),
        (4, 'Complex'),
        (5, 'Enterprise'),
    )

    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    system_id = models.CharField(
        max_length=10, blank=True,
        help_text="System identifier (e.g. SYS-001)"
    )
    subtitle = models.CharField(max_length=200, blank=True)
    excerpt = models.TextField(
        blank=True,
        help_text="Brief summary for display on project cards"
    )
    featured = models.BooleanField(
        default=False, help_text="Feature this project on the homepage")
    
    # Content Fields
    content = MarkdownxField()
    challenges = MarkdownxField(blank=True)
    solutions = MarkdownxField(blank=True)
    outcome = MarkdownxField(blank=True)

    # Technical Details
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    demo_url = models.URLField(blank=True)
    completion_percent = models.IntegerField(
        default=100,
        help_text="Completion percentage (0-100)"
    )
    complexity = models.IntegerField(
        choices=COMPLEXITY_CHOICES,
        default=2,
        help_text="Project Complexity level"
    )

    # Relationship Fields
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="systems"
    )
    system_type = models.ForeignKey(
        SystemType, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="systems"
    )
    technologies = models.ManyToManyField(
        Technology, blank=True, related_name="systems"
    )
    related_projects = models.ManyToManyField(
        'self', blank=True,
        verbose_name="Related Systems"
    )

    # Media Fields
    thumbnail = models.ImageField(
        upload_to="projects/thumbnails/", null=True, blank=True,
        help_text="Thumbnail image (400x300px recommended)"
    )
    banner_image = models.ImageField(
        upload_to="projects/banners/",
        null=True,
        blank=True,
        help_text="Header banner image (1200x400px recommended)",
    )
    featured_image = models.ImageField(
        upload_to="projects/featured/",
        null=True,
        blank=True,
        help_text="Featured image for homepage (800x600px recommended)",
    )

    # Meta Fields
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='draft'
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("projects:system_detail", args=[self.slug])
 
    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.title)

        # Auto-generate system_id if not provided
        if not self.system_id:
            # Get count of existing system and increment
            count = SystemModule.objects.count()
            self.system_id = f"SYS-{count+1:03d}"

        # Generate excerpt from content if not provided
        if not self.excerpt and self.content:
            # Strip markdown and get first 150 characters
            plain_text = re.sub(r"#|\*|\[|\]|\(|\)|_|`", "", self.content)
            self.excerpt = (
                plain_text[:150] + "..." if len(plain_text) > 150 else plain_text
            )

        super().save(*args, **kwargs)

    def rendered_content(self):
        """Return content field as HTML with heading IDs for TOC links."""
        html_content = markdownify(self.content)
        soup = BeautifulSoup(html_content, 'html.parser')

        # Add IDs to headings for TOC
        for h in soup.find_all(["h2", "h3", "h4", "h5", "h6"]):
            if not h.get("id"):
                h["id"] = slugify(h.get_text())

        return str(soup)

    def rendered_challenges(self):
        """Return challenges field as HTML."""
        return markdownify(self.challenges)

    def rendered_solutions(self):
        """Return solutions field as HTML."""
        return markdownify(self.solutions)

    def rendered_outcome(self):
        """Return outcome field as HTML."""
        return markdownify(self.outcome)

    def get_technology_colors(self):
        """Return a list of technology color codes for this project."""
        return [tech.color for tech in self.technologies.all()]

    def is_in_progress(self):
        """Check if the project is still in progress."""
        return self.completion_percent < 100

    def get_log_entries(self):
        """Get all related log entries ordered by priority and date"""
        return (
            self.log_entries.all()
            .select_related("post")
            .order_by("-priority", "-logged_at")
        )

    def get_development_logs(self):
        """Get development-specific log entries"""
        return self.log_entries.filter(connection_type="development").select_related(
            "post"
        )

    def get_latest_log_entry(self):
        """Get the most recent log entry"""
        return self.log_entries.first()

    def get_log_completion_impact(self):
        """Calculate total completion impact from all logs"""
        return (
            self.log_entries.aggregate(total_impact=models.Sum("completion_impact"))[
                "total_impact"
            ]
            or 0
        )


class SystemImage(models.Model):
    """Additional images for a system/project."""

    system = models.ForeignKey(
        SystemModule, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to='projects/gallery/')
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.system.title}"


class SystemFeature(models.Model):
    """Key features for a system/project."""

    system = models.ForeignKey(
        SystemModule, on_delete=models.CASCADE, related_name='features'
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(
        max_length=50, blank=True,
        help_text="Font Awesome icon name (e.g. fa-check)"
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title
