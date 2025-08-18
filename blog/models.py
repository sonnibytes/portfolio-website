from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils import timezone
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
import re
from bs4 import BeautifulSoup


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
        help_text="Programming language for syntax highlighting")
    show_toc = models.BooleanField(
        default=True, help_text="Show table of contents on post page")
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
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
    # Connection to Systems/Projects
    related_systems = models.ManyToManyField(
        "projects.SystemModule",
        through="SystemLogEntry",
        blank=True,
        related_name="related_posts",
        help_text="Systems this log entry relates to",
    )

    class Meta:
        ordering = ['-published_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        """Custom save method to handle published_date and other auto-fields."""

        # Check if this is a new post or status change
        is_new = not self.pk
        old_status = None

        if not is_new:
            try:
                old_post = Post.objects.get(pk=self.pk)
                old_status = old_post.status
            except Post.DoesNotExist:
                old_status = "draft"

        # Set published_date when publishing for the first time
        if (self.status == "published" and old_status != "published" and not self.published_date):
            self.published_date = timezone.now()

        # Clear published_date if moving back to draft
        elif self.status == "draft" and old_status == "published":
            self.published_date = None

        # Auto-generate slug if not provided
        if not self.slug and self.title:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            # Ensure slug uniqueness
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        # Calculate reading time
        if self.content:
            # Avg reading speed: 200 words per minute
            word_count = len(re.findall(r'\w+', self.content))
            self.reading_time = max(1, round(word_count / 200))

        # Generate excerpt from content if not provided
        if not self.excerpt and self.content:
            # Strip markdown and get first 150 characters
            plain_text = re.sub(r'#|\*|\[|\]|\(|\)|_|`', '', self.content)
            self.excerpt = plain_text[:150] + '...' if len(plain_text) > 150 else plain_text

        super(Post, self).save(*args, **kwargs)

    def rendered_content(self):
        """Return content field as HTML with heading IDs for TOC links."""
        html_content = markdownify(self.content)
        soup = BeautifulSoup(html_content, 'html.parser')

        # Add IDs to headings
        for h in soup.find_all(['h2', 'h3', 'h4', 'h5', 'h6']):
            if not h.get('id'):
                h['id'] = slugify(h.get_text())

        return str(soup)

    def get_code_filename(self):
        """Return suitable filename for featured codeblock based on content."""
        # Map code formats to appropriate filenames
        format_to_filename = {
            'python': 'example.py',
            'javascript': 'script.js',
            'html': 'index.html',
            'css': 'styles.css',
            'terminal': 'terminal.sh',
            'markdown': 'readme.md',
            'json': 'data.json',
            'sql': 'query.sql',
            'bash': 'script.sh',
            'plaintext': 'file.txt',
        }
        # Return the appropriate filename based on format
        return format_to_filename.get(self.featured_code_format, 'code.txt')

    # Think I can delete this method? Commenting out and seeing if errors
    # def get_icon_text(self):
    #     """Return text to display as icon if no image available."""
    #     # Mapping of category codes to custom display text
    #     category_to_icon = {
    #         "LJ": "📚",  # Learning Journey - book emoji
    #         "TD": "🔍",  # Technical Deep Dive - magnifying glass
    #         "PD": "📋",  # Project Documentation - clipboard
    #         "CT": "🚀",  # Career Transition - rocket
    #         "NS": "💡",  # Neural Sparks - light bulb
    #     }

    #     # Return the mapped icon text or category code
    #     return category_to_icon.get(self.category.code, self.category.code)

    def get_headings(self):
        """Extract headings from markdown content for table of contents."""
        headings = []
        # Regular expression to find headings in markdown
        heading_pattern = r'^(#{1,3})\s+(.+)$'

        for line in self.content.split('\n'):
            match = re.match(heading_pattern, line.strip())
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()
                # Create an ID from heading text for anchor links
                heading_id = slugify(text)
                headings.append({
                    'level': level,
                    'text': text,
                    'id': heading_id,
                })

        return headings

    def get_system_connections(self):
        """Get all system connection with metadata."""
        return self.system_connections.all().select_related("system")

    def get_primary_system(self):
        """Get the highest priority system connection"""
        connection = self.system_connections.order_by(
            "-priority", "-completion_impact"
        ).first()
        return connection.system if connection else None

    def get_system_connections_by_type(self):
        """Get all system connections grouped by type."""
        connections = {}
        for connection in self.system_connections.all():
            conn_type = connection.connection_type
            if conn_type not in connections:
                connections[conn_type] = []
            connections[conn_type].append(connection)
        return connections

    def has_system_connections(self):
        """Check if post has any system connections."""
        return self.system_connections.exists()

    def get_related_systems(self):
        """Get all related systems for this post."""
        return [conn.system for conn in self.system_connections.all()]

    # Handle Series
    def is_in_series(self):
        """Check if post is part of a series."""
        return SeriesPost.objects.filter(post=self).exists()

    def get_series(self):
        """Get the series this post belongs to, if any."""
        series_post = SeriesPost.objects.filter(post=self).first()
        if series_post:
            return series_post.series
        return None

    def get_series_order(self):
        """Get the order of this post in its series, if any."""
        series_post = SeriesPost.objects.filter(post=self).first()
        if series_post:
            return series_post.order
        return None

    def get_similar_posts(self, count=3):
        """Get simimlar posts based on tags."""
        post_tags_ids = self.tags.values_list('id', flat=True)
        similar_posts = Post.objects.filter(
            tags__in=post_tags_ids,
            status='published'
        ).exclude(id=self.id).distinct()

        # Return posts ordered by number of matching tags
        return similar_posts.annotate(
            same_tags=models.Count('tags')
        ).order_by('-same_tags')[:count]


class Comment(models.Model):
    """Model for blog post comments."""
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.name} on {self.post}"

    def get_absolute_url(self):
        return reverse("blog:comment", args=[self.pk])


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

    def get_absolute_url(self):
        return f"{self.post.get_absolute_url()}#view-{self.pk}"


class Series(models.Model):
    """Model for creating blog post series."""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    # Visual Enhancement
    thumbnail = models.ImageField(upload_to="blog/series/", null=True, blank=True, help_text="Series thumbnail image (400x300px recommended)")

    # Auto-calculated metrics
    post_count = models.IntegerField(default=0, help_text="Number of posts in series (auto-calculated)")
    total_reading_time = models.IntegerField(default=0, help_text="Total reading time for all posts in series (auto-calculated)")

    # Series Metadata
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
            ('expert', 'Expert'),
        ],
        default='intermediate'
    )

    # Status Tracking
    is_complete = models.BooleanField(default=False, help_text="Is this series complete or ongoing?")

    # Visibility
    is_featured = models.BooleanField(default=False, help_text="Feature this series prominently")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

    def update_metrics(self):
        """Update post_count and total_reading_time"""
        posts = self.posts.all()
        self.post_count = posts.count()
        self.total_reading_time = sum(post.post.reading_time for post in posts)
        self.save()

    def get_progress_percentage(self):
        """Get completion percentage if series has target post count"""
        # This oculd be enhanced w a target_posts field
        if hasattr(self, 'target_posts') and self.target_posts:
            return min(100, (self.post_count / self.target_posts) * 100)
        return 100 if self.is_complete else 0

    def get_next_post(self, current_post):
        """Get next post in series after current_post"""
        try:
            current_series_post = self.posts.get(post=current_post)
            next_series_post = self.posts.filter(
                order__gt=current_series_post.order
            ).first()
            return next_series_post.post if next_series_post else None
        except:
            return None

    def get_previous_post(self, current_post):
        """Get previous post in series before current_post"""
        try:
            current_series_post = self.posts.get(post=current_post)
            prev_series_post = self.posts.filter(
                order__lt=current_series_post.order
            ).last()
            return prev_series_post.post if prev_series_post else None
        except:
            return None


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

    def get_absolute_url(self):
        return f"{self.series.get_absolute_url()}#post-{self.pk}"


# Connection to Systems/Projects
class SystemLogEntry(models.Model):
    """
    Enhanced connection model between blog posts and systems with HUD-style metadata.
    Represents how a DataLogs entry relates to a specific system/project.
    """

    CONNECTION_TYPES = (
        ("development", "Development Log"),
        ("documentation", "Technical Documentation"),
        ("analysis", "System Analysis"),
        ("update", "System Update"),
        ("troubleshooting", "Troubleshooting"),
        ("review", "System Review"),
        ("enhancement", "Feature Enhancement"),
        ("deployment", "Deployment Log"),
        ("testing", "Testing Results"),
        ("performance", "Performance Analysis"),
        ("security", "Security Assessment"),
        ("integration", "Integration Notes"),
    )

    PRIORITY_LEVELS = (
        (1, "Low"),
        (2, "Normal"),
        (3, "High"),
        (4, "Critical"),
    )

    LOG_STATUS = (
        ("draft", "Draft"),
        ("active", "Active"),
        ("resolved", "Resolved"),
        ("archived", "Archived"),
    )

    post = models.ForeignKey(
        "Post", on_delete=models.CASCADE, related_name="system_connections"
    )
    system = models.ForeignKey(
        "projects.SystemModule", on_delete=models.CASCADE, related_name="log_entries"
    )

    # Connection metadata
    connection_type = models.CharField(
        max_length=20, choices=CONNECTION_TYPES, default="development"
    )
    priority = models.IntegerField(choices=PRIORITY_LEVELS, default=2)
    log_status = models.CharField(
        max_length=20,
        choices=LOG_STATUS,
        default='active'
    )

    # HUD-style identifiers
    log_entry_id = models.CharField(
        max_length=20, blank=True, help_text="Auto-generated log entry ID (e.g. SYS-001-LOG-042)"
    )

    # Timestamps for the HUD feel
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this log entry was resolved/completed."
    )

    # Impact metrics
    system_version = models.CharField(
        max_length=20, blank=True, help_text="System version this log relates to (e.g. v1.2.3)"
    )

    # Impact assessment
    impact_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low Impact'),
            ('medium', 'Medium Impact'),
            ('high', 'High Impact'),
            ('critical', 'Critical Impact'),
        ],
        default='medium'
    )

    # Time tracking
    estimated_hours = models.IntegerField(null=True, blank=True, help_text="Estimated hours to complete this work")
    actual_hours = models.IntegerField(null=True, blank=True, help_text="Actual hours spent on this work")

    completion_impact = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="How much this log entry contributed to project completion (%)",
    )

    # Technical details
    affected_components = models.CharField(
        max_length=200,
        blank=True,
        help_text="Comma-separated list of affected system components"
    )

    # Resolution Tracking
    resolution_notes = models.TextField(blank=True, help_text="Notes on how this issue was resolved")

    # For HUD dashboard display
    performance_impact = models.CharField(
        max_length=20,
        choices=[
            ('positive', 'Positive Impact'),
            ('negative', 'Negative Impact'),
            ('neutral', 'No Impact'),
            ('unknown', 'Unknown'),
        ],
        default='neutral'
    )

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["post", "system"]
        verbose_name = "System Log Entry"
        verbose_name_plural = "System Log Entries"

    def save(self, *args, **kwargs):
        if not self.log_entry_id:
            # Generate HUD-style log entry ID
            count = SystemLogEntry.objects.filter(system=self.system).count()
            self.log_entry_id = f"{self.system.system_id}-LOG-{count + 1:03d}"

        # Auto-resolve based on post status
        if self.post.status == 'published' and self.log_status == 'draft':
            self.log_status = 'active'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.log_entry_id}: {self.post.title}"

    def get_status_color(self):
        """Return color based on priority for HUD styling"""
        if self.log_status == 'resolved':
            return '#27c93f'  # Green
        elif self.log_status == 'archived':
            return '#666666'  # Gray

        # Priority-based colors for active logs
        colors = {
            1: "#5edfff",  # Low - Light Blue
            2: "#00f0ff",  # Normal - Cyan
            3: "#ffbd2e",  # High - Yellow
            4: "#ff6b8b",  # Critical - Coral
        }
        return colors.get(self.priority, "#00f0ff")

    def get_connection_icon(self):
        """Return appropriate icon for connection type."""
        icons = {
            "development": "fa-code",
            "documentation": "fa-file-alt",
            "analysis": "fa-chart-line",
            "update": "fa-sync-alt",
            "troubleshooting": "fa-bug",
            "review": "fa-search",
            "enhancement": "fa-plus-circle",
            "deployment": "fa-rocket",
            "testing": "fa-vial",
            "performance": "fa-tachometer-alt",
            "security": "fa-shield-alt",
            "integration": "fa-plug",
        }
        return icons.get(self.connection_type, "fa-file-alt")

    def get_affected_components_list(self):
        """Return affected components as a list"""
        if self.affected_components:
            return [comp.strip() for comp in self.affected_components.split(",")]
        return []

    def hours_variance(self):
        """Calculate difference between estimated and actual hours"""
        if self.estimated_hours and self.actual_hours:
            return self.actual_hours - self.estimated_hours
        return None

    def get_impact_color(self):
        """Return color for impact level display"""
        colors = {
            "low": "#27c93f",
            "medium": "#ffbd2e",
            "high": "#ff8a80",
            "critical": "#f44336",
        }
        return colors.get(self.impact_level, "#00f0ff")

    def get_absolute_url(self):
        return f"{self.post.get_absolute_url()}#log-{self.pk}"
