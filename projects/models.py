from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
import re
from bs4 import BeautifulSoup

"""
ENHANCED SYSTEM ARCHITECTURE MODELS
System Type > System Module > System Features/Images
Connected to Blog via SystemLogEntry
"""


class Technology(models.Model):
    """Technology/Stack model for categorizing project technologies."""
    CATEGORY_CHOICES = (
        ('language', 'Programming Language'),
        ('framework', 'Framework/Library'),
        ('database', 'Database'),
        ('cloud', 'Cloud Service'),
        ('tool', 'Development Tool'),
        ('other', 'Other'),
    )

    # Base info
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, default="other"
    )

    # Visual Properties
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Font Awesome icon name (e.g., fa-python)"
    )
    color = models.CharField(
        max_length=7,
        default="#00f0ff",
        help_text="Hex color code for HUD display(e.g., #00f0ff)"
    )

    class Meta:
        verbose_name_plural = "technologies"
        ordering = ['category', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("projects:technology", args=[self.slug])


class SystemType(models.Model):
    """System Type model for categorizing projects/systems."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    code = models.CharField(max_length=4,
                            help_text="Short code for display in hexagon (e.g., ML, WEB, API, DATA)")
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7,
                             default="#00f0ff",
                             help_text="Hex color code for HUD accent (e.g., #00f0ff)")
    icon = models.CharField(
        max_length=50, blank=True,
        help_text="Font Awesome icon name (e.g. fa-robot)"
    )
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "system types"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("projects:system_type", args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_systems_count(self):
        """Get count of published systems in this type."""
        return self.systems.filter(status='published').count()


class SystemModule(models.Model):
    """System Module model (Project model)."""

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('in_development', 'In Development'),
        ('testing', 'Testing Phase'),
        ('deployed', 'Deployed'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )

    COMPLEXITY_CHOICES = (
        (1, 'Basic'),
        (2, 'Intermediate'),
        (3, 'Advanced'),
        (4, 'Complex'),
        (5, 'Enterprise'),
    )

    PRIORITY_CHOICES = (
        (1, 'Low'),
        (2, 'Normal'),
        (3, 'High'),
        (4, 'Critical'),
    )

    # ================= BASIC INFORMATION =================
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    system_id = models.CharField(
        max_length=10, blank=True,
        help_text="Auto-generated system identifier (e.g. SYS-001)"
    )
    subtitle = models.CharField(max_length=200, blank=True)
    excerpt = models.TextField(
        blank=True,
        help_text="Brief summary for display on system cards"
    )
    featured = models.BooleanField(
        default=False, help_text="Feature this system on the homepage")

    # ================= CONTENT FIELDS =================
    description = MarkdownxField(
        help_text="Main system description and overview"
    )
    features_overview = MarkdownxField(
        blank=True,
        help_text="Key features and capabilities"
    )
    technical_details = MarkdownxField(
        blank=True,
        help_text="Technical implementation details"
    )
    challenges = MarkdownxField(
        blank=True,
        help_text="Development challenges and solutions"
    )
    future_enhancements = MarkdownxField(
        blank=True,
        help_text="Planned improvement and roadmap"
    )

    # ================= TECHNICAL DETAILS =================
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True,
                               help_text="Live demo/deployment URL")
    demo_url = models.URLField(blank=True,
                               help_text="Interactive demo URL")
    documentation_url = models.URLField(blank=True)

    # System metrics
    completion_percent = models.IntegerField(
        default=100,
        help_text="Development completion percentage (0-100)"
    )
    complexity = models.IntegerField(
        choices=COMPLEXITY_CHOICES,
        default=2,
        help_text="System Complexity level"
    )
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=2,
        help_text="Development priority"
    )

    # Performance metrics (for HUD display)
    performance_score = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Performance score (0.0-100.0)"
    )
    uptime_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="System uptime percentage"
    )

    # ================= RELATIONSHIP FIELDS =================
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
    related_systems = models.ManyToManyField(
        'self', blank=True,
        verbose_name="Related Systems",
        help_text="Other systems that integrate with this one"
    )

    # ================= MEDIA FIELDS =================
    thumbnail = models.ImageField(
        upload_to="systems/thumbnails/", null=True, blank=True,
        help_text="System card thumbnail (400x300px recommended)"
    )
    banner_image = models.ImageField(
        upload_to="systems/banners/",
        null=True,
        blank=True,
        help_text="System header banner (1200x400px recommended)",
    )
    featured_image = models.ImageField(
        upload_to="systems/featured/",
        null=True,
        blank=True,
        help_text="Featured image for homepage (800x600px recommended)",
    )
    architecture_diagram = models.ImageField(
        upload_to="systems/diagrams/",
        null=True,
        blank=True,
        help_text="System architecture diagram"
    )

    # ================= META FIELDS =================
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='draft'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_date = models.DateField(
        blank=True,
        null=True,
        help_text="Development start date"
    )
    end_date = models.DateField(
        blank=True,
        null=True,
        help_text="Development completion date"
    )
    deployment_date = models.DateField(
        blank=True,
        null=True,
        help_text="Production deployment date"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "System Module"
        verbose_name_plural = "System Modules"

    def __str__(self):
        return f"{self.system_id}: {self.title}"

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
            self.system_id = f"SYS-{count + 1:03d}"

        # Generate excerpt from content if not provided
        if not self.excerpt and self.description:
            # Strip markdown and get first 150 characters
            plain_text = re.sub(r"#|\*|\[|\]|\(|\)|_|`", "", self.description)
            self.excerpt = (
                plain_text[:150] + "..." if len(plain_text) > 150 else plain_text
            )

        super().save(*args, **kwargs)

    def rendered_content(self):
        """Return description field as HTML with heading IDs for TOC links."""
        html_content = markdownify(self.description)
        soup = BeautifulSoup(html_content, 'html.parser')

        # Add IDs to headings for TOC
        for h in soup.find_all(["h2", "h3", "h4", "h5", "h6"]):
            if not h.get("id"):
                h["id"] = slugify(h.get_text())

        return str(soup)

    def render_technical_details(self):
        """Return technical details as HTML."""
        return markdownify(self.technical_details)

    def rendered_challenges(self):
        """Return challenges field as HTML."""
        return markdownify(self.challenges)

    def rendered_future_enhancements(self):
        """Return future enhancements field as HTML."""
        return markdownify(self.future_enhancements)

    def get_technology_colors(self):
        """Return a list of technology color codes for this System."""
        return [tech.color for tech in self.technologies.all()]

    def is_in_development(self):
        """Check if the system is still in development."""
        return self.status in ['draft', 'in_development', 'testing']

    def is_live(self):
        """Check if system is deployed and live."""
        return self.status in ['deployed', 'published']

    def get_status_color(self):
        """Return status color for HUD display."""
        status_colors = {
            "draft": "#808080",  # Gray
            "in_development": "#ffbd2e",  # Yellow
            "testing": "#ff6b8b",  # Coral
            "deployed": "#27c93f",  # Green
            "published": "#00f0ff",  # Cyan
            "archived": "#666666",  # Dark Gray
        }
        return status_colors.get(self.status, "#00f0ff")

    def get_complexity_display(self):
        """Return complexity as a visual indicator."""
        return "●" * self.complexity + "○" * (5 - self.complexity)

    def get_related_logs(self):
        """Get all related system logs ordered by priority and date"""
        return (
            self.log_entries.all()
            .select_related("post")
            .order_by("-priority", "-created_at")
        )

    def get_latest_log_entry(self):
        """Get the most recent system log."""
        return self.log_entries.first()

    def get_development_progress(self):
        """Calculate development progress based on various factors."""
        if self.completion_percent:
            return self.completion_percent

        # Calculate based on status if no explicit percentage
        status_progress = {
            'draft': 10,
            'in_development': 40,
            'testing': 80,
            'deployed': 95,
            'published': 100,
            'archived': 100,
        }
        return status_progress.get(self.status, 0)


class SystemImage(models.Model):
    """Additional images for a system (gallery, screenshots, etc)."""

    IMAGE_TYPES = (
        ('screenshot', 'Screenshot'),
        ('diagram', 'Diagram'),
        ('workflow', 'Workflow'),
        ('ui', 'User Interface'),
        ('architecture', 'Architecture'),
        ('demo', 'Demo'),
        ('other', 'Other'),
    )

    system = models.ForeignKey(
        SystemModule, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to='systems/gallery/')
    caption = models.CharField(max_length=255, blank=True)
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="Alt text for accessibility"
    )
    image_type = models.CharField(
        max_length=20,
        choices=IMAGE_TYPES,
        default='screenshot'
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.image_type.title()} for {self.system.title}"

    def get_absolute_url(self):
        return f"{self.system.get_absolute_url()}#image-{self.pk}"


class SystemFeature(models.Model):
    """Key features for a system with HUD-style display."""

    FEATURE_TYPES = (
        ('core', 'Core Feature'),
        ('advanced', 'Advanced Feature'),
        ('integration', 'Integration'),
        ('performance', 'Performance'),
        ('security', 'Security'),
        ('ui', 'User Interface'),
    )

    IMPLEMENTATION_STATUSES = (
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('tested', 'Tested'),
    )

    system = models.ForeignKey(
        SystemModule, on_delete=models.CASCADE, related_name='features'
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(
        max_length=50, blank=True,
        help_text="Font Awesome icon name (e.g. fa-check)"
    )
    feature_type = models.CharField(
        max_length=20,
        choices=FEATURE_TYPES,
        default='core'
    )
    implementation_status = models.CharField(
        max_length=20,
        choices=IMPLEMENTATION_STATUSES,
        default='completed'
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.title} ({self.system.title})"

    def get_status_color(self):
        """Return status color for HUD display."""
        colors = {
            "planned": "#808080",
            "in_progress": "#ffbd2e",
            "completed": "#27c93f",
            "tested": "#00f0ff",
        }
        return colors.get(self.implementation_status, "#00f0ff")

    def get_absolute_url(self):
        return f"{self.system.get_absolute_url()}#feature-{self.pk}"


class SystemMetric(models.Model):
    """Performance and operational metrics for HUD dashboard display."""

    METRIC_TYPES = (
        ('performance', 'Performace'),
        ('usage', 'Usage'),
        ('uptime', 'Uptime'),
        ('response_time', 'Response Time'),
        ('throughput', 'Throughput'),
        ('error_rate', 'Error Rate'),
        ('custom', 'Custom'),
    )

    system = models.ForeignKey(
        SystemModule,
        on_delete=models.CASCADE,
        related_name='metrics'
    )
    metric_name = models.CharField(max_length=100)
    metric_value = models.DecimalField(max_digits=10, decimal_places=2)
    metric_unit = models.CharField(
        max_length=20,
        blank=True,
        help_text="Unit of measurement (%, ms, MB, etc)"
    )
    metric_type = models.CharField(
        max_length=20,
        choices=METRIC_TYPES,
        default='performance'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_current = models.BooleanField(
        default=True,
        help_text="Whether this is current/latest metric value"
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.system.system_id} - {self.metric_name}: {self.metric_value}{self.metric_unit}"

    def save(self, *args, **kwargs):
        if self.is_current:
            # Set all other metrics of the same type to not current
            SystemMetric.objects.filter(
                system=self.system,
                metric_name=self.metric_name
            ).update(is_current=False)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"{self.system.get_absolute_url()}#metric-{self.pk}"
