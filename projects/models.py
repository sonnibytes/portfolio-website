from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
import re
from bs4 import BeautifulSoup
from datetime import date, timedelta
from django.db.models import Avg, Count
from django.utils import timezone


"""
ENHANCED SYSTEM ARCHITECTURE MODELS
System Type > System Module > System Features/Images
Connected to Blog via SystemLogEntry
"""


class SystemModuleQuerySet(models.QuerySet):
    """Custom queryset for SystemModule w useful filters."""

    def deployed(self):
        return self.filter(status='deployed')

    def published(self):
        return self.filter(status='published')

    def in_development(self):
        return self.filter(status='in_development')

    def featured(self):
        return self.filter(featured=True)

    def with_performance_data(self):
        return self.filter(
            performance_score__isnull=False,
            uptime_percentage__isnull=False
        )

    def high_priority(self):
        return self.filter(priority__in=[3, 4])  # High and Critical

    def recently_updated(self, days=7):
        return self.filter(
            updated_at__gte=timezone.now() - timedelta(days=days)
        )


class SystemModuleManager(models.Manager):
    """Custom Manager for SystemModule."""

    def get_queryset(self):
        return SystemModuleQuerySet(self.model, using=self._db)

    def deployed(self):
        return self.get_queryset().deployed()

    def published(self):
        return self.get_queryset().published()

    def in_development(self):
        return self.get_queryset().in_development()

    def featured(self):
        return self.get_queryset().featured()

    def with_performance_data(self):
        return self.get_queryset().with_performance_data()

    def recently_updated(self, days=7):
        return self.get_queryset().recently_updated(days)

    def high_priority(self):
        return self.get_queryset().high_priority()

    def dashboard_stats(self):
        """Get key dashboard statistics."""
        return {
            'total_systems': self.count(),
            'deployed_count': self.deployed().count(),
            'published_count': self.published().count(),
            'in_development_count': self.in_development().count(),
            'featured_count': self.featured().count(),
            'avg_completion': self.aggregate(
                avg=Avg('completion_percent')
            )['avg'] or 0,
            'avg_performance': self.with_performance_data().aggregate(
                avg=Avg('performance_score')
            )['avg'] or 0,
        }


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
        # ('idea', 'Idea'),
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

    # ================= CONTENT FIELDS =================
    description = MarkdownxField(
        help_text="Full project description in Markdown"
    )
    features_overview = MarkdownxField(
        blank=True, help_text="Key features and capabilities overview"
    )
    technical_details = MarkdownxField(
        blank=True,
        help_text="Technical implementation details"
    )
    challenges = MarkdownxField(
        blank=True,
        help_text="Development challenges faced and how they were overcome"
    )
    future_enhancements = MarkdownxField(
        blank=True,
        help_text="Planned improvement and next steps"
    )

    # ================= CATEGORIZATION =================
    system_type = models.ForeignKey(
        SystemType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="systems",
    )
    technologies = models.ManyToManyField(
        Technology, blank=True, related_name="systems"
    )
    complexity = models.IntegerField(
        choices=COMPLEXITY_CHOICES, default=2, help_text="System Complexity level"
    )
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES, default=2, help_text="Development priority"
    )

    # ================= PROJECT STATUS =================
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    featured = models.BooleanField(default=False)
    completion_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=100, help_text="Completion percentage (0-100)"
    )

    # ================= PERFORMANCE METRICS =================
    performance_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Performance score (0-100)",
    )
    uptime_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="System uptime percentage",
    )

    response_time_ms = models.IntegerField(default=0, help_text="Average response time in milliseconds")
    daily_users = models.IntegerField(default=0, help_text="Average daily active users")

    # ================= DEVELOPMENT TRACKING METRICS =================
    code_lines = models.PositiveIntegerField(default=0, help_text="Total lines of code")
    commit_count = models.PositiveIntegerField(default=0, help_text="Total Git commits")
    last_commit_date = models.DateTimeField(null=True, blank=True, help_text="Date of last Git commit")

    # ================= PROJECT TIMELINE =================
    estimated_completion_date = models.DateField(null=True, blank=True, help_text="Estimated project completion")

    # ================= RESOURCE TRACKING =================
    estimated_dev_hours = models.IntegerField(null=True, blank=True, help_text="Estimated development hours")
    actual_dev_hours = models.IntegerField(null=True, blank=True, help_text="Actual development hours spent")

    # ================= COLLABORATION =================
    team_size = models.IntegerField(default=1, help_text="Number of team members")

    # ================= LINKS AND RESOURCES =================
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True, help_text="Live demo/deployment URL")
    demo_url = models.URLField(blank=True, help_text="Interactive demo URL")
    documentation_url = models.URLField(blank=True)

    # ================= VISUAL ASSETS =================
    thumbnail = models.ImageField(
        upload_to="systems/thumbnails/",
        null=True,
        blank=True,
        help_text="System card thumbnail (400x300px recommended)",
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
        help_text="System architecture diagram",
    )

    # ================= METADATA =================
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="systems")
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

    # ================= LEARNING-FOCUSED ADDITIONS =================

    # Learning Stage Classification
    LEARNING_STAGE_CHOICES = (
        ('tutorial', 'Following Tutorial'),
        ('guided', 'Guided Project'),
        ('independent', 'Independent Development'),
        ('refactoring', 'Refactoring/Improving'),
        ('contributing', 'Open Source Contributing'),
        ('teaching', 'Teaching/Sharing'),
    )

    learning_stage = models.CharField(max_length=20, choices=LEARNING_STAGE_CHOICES, default='independent', help_text='What stage of learning was this project for you?')

    # Skill Development Connection
    skills_developed = models.ManyToManyField(
        "core.Skill",
        through='SystemSkillGain',
        blank=True,
        related_name='developed_in_projects',
        help_text="Skills gained or improved through this project"
    )

    # Portfolio Assessment
    portfolio_ready = models.BooleanField(default=False, help_text="Is this project ready to show to potential employers?")

    # ================= CUSTOM MANAGER =================
    objects = SystemModuleManager()

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

    # ================= CONTENT RENDERING METHODS =================
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

    # ================= STATUS AND HEALTH METHODS =================
    def get_health_status(self):
        """Return system health based on metrics"""
        if not self.uptime_percentage:
            return "unknown"

        uptime = float(self.uptime_percentage)
        if uptime >= 99.9:
            return "excellent"
        elif uptime >= 99.0:
            return "good"
        elif uptime >= 95.0:
            return "fair"
        else:
            return "poor"

    def get_response_status(self):
        """Return response time status"""
        if self.response_time_ms <= 100:
            return "excellent"
        elif self.response_time_ms <= 300:
            return "good"
        elif self.response_time_ms <= 1000:
            return "fair"
        else:
            return "poor"

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

    def get_development_progress(self):
        """Calculate development progress based on various factors."""
        if self.completion_percent:
            return self.completion_percent

        # Calculate based on status if no explicit percentage
        status_progress = {
            "draft": 10,
            "in_development": 40,
            "testing": 80,
            "deployed": 95,
            "published": 100,
            "archived": 100,
        }
        return status_progress.get(self.status, 0)

    def hours_variance(self):
        """Calculate hours over/under estimate"""
        if self.estimated_dev_hours and self.actual_dev_hours:
            return self.actual_dev_hours - self.estimated_dev_hours
        return None

    def completion_trend(self):
        """Predict completion based on current progress"""
        if self.estimated_completion_date and self.completion_percent:
            days_remaining = (self.estimated_completion_date - date.today()).days
            if self.completion_percent >= 90:
                return "on_track"
            elif days_remaining < 0:
                return "overdue"
            elif self.completion_percent < 50 and days_remaining < 30:
                return "at_risk"
            else:
                return "on_track"
        return "unknown"

    def get_technology_colors(self):
        """Return a list of technology color codes for this System."""
        return [tech.color for tech in self.technologies.all()]

    def is_in_development(self):
        """Check if the system is still in development."""
        return self.status in ['draft', 'in_development', 'testing']

    def is_live(self):
        """Check if system is deployed and live."""
        return self.status in ['deployed', 'published']

    def get_complexity_stars(self):
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

    # ================= NEW ENHANCED METHODS FOR DASHBOARD =================
    def get_status_badge_color(self):
        """Get color class based on system status for badges."""
        status_colors = {
            'deployed': 'success',
            'published': 'success',
            'in_development': 'warning',
            'testing': 'info',
            'maintenance': 'warning',
            'draft': 'seccondary',
            'archived': 'muted',
        }
        return status_colors.get(self.status, 'secondary')

    def get_priority_color(self):
        """Get color class based on priority level."""
        priority_colors = {
            1: 'success',   # Low - green
            2: 'info',      # Normal - blue
            3: 'warning',   # High - yellow
            4: 'danger',    # Critical - red
        }
        return priority_colors.get(self.priority, 'info')

    def get_progress_color(self):
        """Get color class based on completion progress."""
        if not self.completion_percent:
            return 'secondary'

        if self.completion_percent >= 90:
            return 'success'
        elif self.completion_percent >= 70:
            return 'info'
        elif self.completion_percent >= 50:
            return 'warning'
        else:
            return 'danger'

    def get_complexity_display(self):
        """Get human-readable complexity display with visual indiccators."""
        complexity_map = {
            1: {'label': 'Basic', 'stars': '★☆☆☆☆', 'color': 'success'},
            2: {'label': 'Intermediate', 'stars': '★★☆☆☆', 'color': 'info'},
            3: {'label': 'Advanced', 'stars': '★★★☆☆', 'color': 'warning'},
            4: {'label': 'Complex', 'stars': '★★★★☆', 'color': 'warning'},
            5: {'label': 'Enterprise', 'stars': '★★★★★', 'color': 'danger'},
        }
        return complexity_map.get(self.complexity, {'label': 'Unknown', 'stars': '☆☆☆☆☆', 'color': 'secondary'})

    def get_technology_summary(self):
        """Get technology stack summary for dashboard display."""
        techs = self.technologies.all()
        return {
            'total_count': techs.count(),
            'primary_techs': techs[:3],  # First 3 as primary
            'color_palette': [tech.color for tech in techs if hasattr(tech, 'color')],
        }

    def get_dashboard_metrics(self):
        """Get all metrics for dashboard display in one call."""
        return {
            'basic_info': {
                'system_id': self.system_id,
                'title': self.title,
                'status': self.status,
                'status_color': self.get_status_badge_color(),
                'complexity': self.get_complexity_display(),
                'priority': self.priority,
                'priority_color': self.get_priority_color(),
            },
            'progress': {
                'completion_percent': self.completion_percent,
                'progress_color': self.get_priority_color(),
                'development_progress': self.get_development_progress(),
            },
            'performance': {
                'health_status': self.get_health_status(),
                'performance_score': self.performance_score,
                'uptime_percentage': self.uptime_percentage,
                'response_status': self.get_response_status(),
                'daily_users': self.daily_users,
            },
            'development': {
                'code_lines': self.code_lines,
                'commit_count': self.commit_count,
                'hours_variance': self.hours_variance(),
                'completion_trend': self.completion_trend(),
            },
        }

    def get_deployment_readiness(self):
        """Calculate deployment readiness score."""
        score = 0
        max_score = 10

        # Basic information completeness (2 pt)
        if self.description and self.title:
            score += 1
        if self.technical_details:
            score += 1

        # Development progress (3 pt)
        if self.completion_percent:
            if self.completion_percent >= 90:
                score += 3
            elif self.completion_percent >= 70:
                score += 2
            elif self.completion_percent >= 50:
                score += 1

        # Testing and quality (2 pt)
        if self.status in ['testing', 'deployed', 'published']:
            score += 1
        if hasattr(self, 'features') and self.features.filter(implementation_status='tested').exists():
            score += 1

        # Documentation and links (2 pt)
        if self.github_url:
            score += 1
        if self.live_url or self.demo_url:
            score += 1

        # Performance metrics (1 pt)
        if self.performance_score and self.uptime_percentage:
            score += 1

        readiness_percent = (score / max_score) * 100

        # Determine readiness status
        if readiness_percent >= 90:
            status = 'ready'
        elif readiness_percent >= 70:
            status = 'almost_ready'
        elif readiness_percent >= 50:
            status = 'in_progress'
        else:
            status = 'not_ready'

        return {
            'score': score,
            'max_score': max_score,
            'percentage': round(readiness_percent, 1),
            'status': status,
        }

    def get_status_icon(self):
        """Return Font Awesome icon for status"""
        icons = {
            'deployed': 'rocket',
            'in_development': 'code',
            'testing': 'vial',
            'updated': 'sync-alt',
        }
        return icons.get(self.status, 'sync-alt')

    # ================= LEARNING-FOCUSED METHODS =================

    def get_learning_velocity(self):
        """Skills gained per month of development"""
        if not self.created_at or not self.skills_developed.exists():
            return 0

        months = max((timezone.now() - self.created_at).days / 30, 1)
        return round(self.skills_developed.count() / months, 2)

    def get_complexity_evolution_score(self):
        """Project complexity based on metrics"""
        tech_score = self.technologies.count() * 2
        loc_score = min(self.code_lines / 1000, 5) if self.code_lines else 0
        commit_score = min(self.commit_count / 50, 3) if self.commit_count else 0

        return round(tech_score + loc_score + commit_score, 1)

    def get_learning_stage_color(self):
        """Color coding for learning stage badges"""
        colors = {
            "tutorial": "#FFB74D",      # Orange - learning basics
            "guided": "#81C784",        # Green - following guidance
            "independent": "#64B5F6",   # Blue - working independently
            "refactoring": "#BA68C8",   # Purple - improving skills
            "contributing": "#4FC3F7",  # Cyan - giving back
            "teaching": "#FFD54F",      # Gold - sharing knowledge
        }
        return colors.get(self.learning_stage, "#64B5F6")

    def get_portfolio_readiness_score(self):
        """Calculate portfolio readiness using existing fields"""
        score = 0

        # Content completeness (40 points)
        if self.description:
            score += 10
        if self.excerpt:
            score += 10
        if self.live_url or self.demo_url:
            score += 10
        if self.github_url:
            score += 10

        # Technical polish (30 points)
        if self.technologies.exists():
            score += 10
        if self.featured_image:
            score += 10
        if self.completion_percent >= 80:
            score += 10

        # Learning documentation via DataLogs (20 points)
        if self.get_related_logs().exists():
            score += 20

        # Manual assessment (10 points)
        if self.portfolio_ready:
            score += 10

        return min(score, 100)

    def get_development_stats_for_learning(self):
        """Learning-focused stats using existing fields"""
        return {
            # Use existing time tracking
            'estimated_hours': self.estimated_dev_hours or 0,
            'actual_hours': self.actual_dev_hours or 0,
            'hours_variance': self.hours_variance() or 0,

            # Use existing code metrics
            'lines_of_code': self.code_lines,
            'commits': self.commit_count,
            'last_commit': self.last_commit_date,

            # New learning metrics
            'skills_count': self.skills_developed.count(),
            'learning_stage': self.get_learning_stage_display(),  # Created by django automatically w choice field
            'learning_velocity': self.get_learning_velocity(),
            'complexity_score': self.get_complexity_evolution_score(),
            'portfolio_ready': self.portfolio_ready,
            'readiness_score': self.get_portfolio_readiness_score(),

            # Use existing status tracking
            'completion_percent': float(self.completion_percent),
            'status': self.status,
            'complexity': self.complexity,
        }

    def get_skills_summary(self):
        """Get comma-sparated skills for cards"""
        skills = list(self.skills_developed.values_list('name', flat=True)[:4])
        if self.skills_developed.count() > 4:
            return f"{', '.join(skills)} +{self.skills_developed.count() - 4} more"
        return ", ".join(skills) if skills else "No skills tracked yet"

    def get_investment_summary(self):
        """Summary of time invested using existing fields"""
        if self.actual_dev_hours:
            return f"{self.actual_dev_hours} hours actual"
        elif self.estimated_dev_hours:
            return f"{self.estimated_dev_hours} hours estimated"
        else:
            # Calculate rough estimate from timeline
            if self.start_date and self.end_date:
                days = (self.end_date - self.start_date).days
                return f"~{days} days development"
            return "Time not tracked"

    def get_time_investment_level(self):
        """Categorize time-investment level"""
        hours = self.actual_dev_hours
        if not hours:
            return "Unknown"

        if hours >= 100:
            return "Major Project"
        elif hours >= 50:
            return "Substantial"
        elif hours >= 20:
            return "Moderate"
        else:
            return "Quick Build"

    def get_learning_documentation_from_logs(self):
        """Extract learning content from related DataLogs"""
        related_logs = self.get_related_logs()

        if not related_logs.exists():
            return None

        learning_docs = {
            'total_posts': related_logs.count(),
            'latest_post': related_logs.first().post if related_logs.exists() else None,
            'development_logs': related_logs.filter(connection_type='development'),
            'documentation_logs': related_logs.filter(connection_type='documentation'),
            'analysis_logs': related_logs.filter(connection_type='analysis'),
        }

        return learning_docs

    def has_learning_documentation(self):
        """Check if learning is documented via DataLogs"""
        return self.get_related_logs().exists()

    def get_github_metrics_summary(self):
        """GitHub activity summary using existing fields"""
        return {
            'repository_url': self.github_url,
            'commits': self.commit_count,
            'lines_of_code': self.code_lines,
            'last_activity': self.last_commit_date,
            'has_repo': bool(self.github_url),
            'active_development': bool(
                self.last_commit_date and self.last_commit_date >= timezone.now() - timedelta(days=30)
            ),
        }

    # ================= TEMPLATE PROPERTIES =================
    @property
    def health_status(self):
        """Property version for easy template access."""
        return self.get_health_status()

    @property
    def progress_color(self):
        """Property version for easy template access."""
        return self.get_progress_color()

    @property
    def status_badge_color(self):
        """Property version for easy template access."""
        return self.get_status_badge_color()

    @property
    def complexity_display(self):
        """Property version for easy template access."""
        return self.get_complexity_display()

    @property
    def dashboard_metrics(self):
        """Property version for easy template access."""
        return self.get_dashboard_metrics()

    @property
    def deployment_readiness(self):
        """Property version for easy template access."""
        return self.get_deployment_readiness()

    # ================= CLASS METHODS FOR BULK OPERATIONS =================
    @classmethod
    def get_health_distribution(cls):
        """Get distribution of systems by health status."""
        systems = cls.objects.all()
        distribution = {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0, 'unknown': 0}

        for system in systems:
            health = system.get_health_status()
            distribution[health] += 1
        return distribution

    @classmethod
    def get_status_statistics(cls):
        """Get comprehensive status statistics."""
        stats = {}
        for status_choice in cls.STATUS_CHOICES:
            status_key = status_choice[0]
            status_label = status_choice[1]

            systems = cls.objects.filter(status=status_key)
            count = systems.count()

            if count > 0:
                avg_completion = systems.aggregate(avg=Avg('completion_percent'))['avg'] or 0
                stats[status_key] = {
                    'label': status_label,
                    'count': count,
                    'avg_completion': round(avg_completion, 1),
                    'systems': systems[:3]  # Sample systems
                }
        return stats


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


class SystemDependency(models.Model):
    """Track dependencies between systems"""

    DEPENDENCY_TYPES = [
        ("api", "API Dependency"),
        ("database", "Database Dependency"),
        ("service", "Service Dependency"),
        ("library", "Library Dependency"),
        ("integration", "Integration Dependency"),
        ("data_flow", "Data Flow"),
        ("authentication", "Authentication Dependency"),
        ("infrastructure", "Infrastructure Dependency"),
    ]

    system = models.ForeignKey(SystemModule, on_delete=models.CASCADE, related_name='dependencies')
    depends_on = models.ForeignKey(SystemModule, on_delete=models.CASCADE, related_name='dependents')
    dependency_type = models.CharField(max_length=20, choices=DEPENDENCY_TYPES, default='integration')
    is_critical = models.BooleanField(default=False, help_text="System cannot function without this dependency")
    description = models.TextField(blank=True, help_text="Description of dependency relationship")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('system', 'depends_on')
        verbose_name_plural = "System Dependencies"

    def __str__(self):
        return f"{self.system.system_id} depends on {self.depends_on.system_id}"

    def get_absolute_url(self):
        return f"{self.system.get_absolute_url()}#dependency-{self.pk}"


class SystemSkillGain(models.Model):
    """
    Through model connecting SystemModule to core.Skill
    Tracks what skills were gained/improved through each project
    Focused on essential learning data only
    """

    PROFICIENCY_GAINED_CHOICES = (
        (1, 'First Exposure'),
        (2, 'Basic Understanding'),
        (3, 'Practical Application'),
        (4, 'Confident Usage'),
        (5, 'Teaching Level'),
    )

    # Core relationships
    system = models.ForeignKey(SystemModule, on_delete=models.CASCADE, related_name='skill_gains')
    skill = models.ForeignKey('core.Skill', on_delete=models.CASCADE, related_name='project_gains')

    # Essentail Learning Data
    proficiency_gained = models.IntegerField(choices=PROFICIENCY_GAINED_CHOICES, help_text="Level of proficiency gained")

    # Optional Context (keep minimal)
    how_learned = models.TextField(blank=True, help_text="Brief note on how this skill was used/learned in this project")

    # Optional before/after tracking
    skill_level_before = models.IntegerField(choices=[(i, i) for i in range(1, 6)], blank=True, null=True, help_text="Skill level before project (1-5, optional)")
    skill_level_after = models.IntegerField(choices=[(i, i) for i in range(1, 6)], blank=True, null=True, help_text="Skill level after project (1-5, optional)")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['system', 'skill']
        ordering = ['-created_at']
        verbose_name = "System Skill Gain"
        verbose_name_plural = "System Skill Gains"

    def __str__(self):
        return f"{self.skill.name} gained in {self.system.title}"

    def get_proficiency_display_short(self):
        """Short display for UI cards"""
        display_map = {
            1: "First Time",
            2: "Learned Basics",
            3: "Applied Practically",
            4: "Gained Confidence",
            5: "Teaching Level"
        }
        return display_map.get(self.proficiency_gained, "Unknokwn")

    def get_proficiency_color(self):
        """Color for proficiency level badges"""
        colors = {
            1: "#FFB74D",  # Orange - first exposure
            2: "#81C784",  # Green - basic understanding
            3: "#64B5F6",  # Blue - practical application
            4: "#BA68C8",  # Purple - confident usage
            5: "#FFD54F",  # Gold - teaching level
        }
        return colors.get(self.proficiency_gained, "#64B5F6")

    def get_skill_improvement(self):
        """Calculate improvement if before/after levels set"""
        if self.skill_level_before and self.skill_level_after:
            return self.skill_level_after - self.skill_level_before
        return None

    def has_improvement_data(self):
        """Check if before/after tracking is available"""
        return bool(self.skill_level_before and self.skill_level_after)

    def get_learning_context(self):
        """Get learning context for dashboard display"""
        return {
            'skill_name': self.skill.name,
            'system_title': self.system.title,
            'proficiency_gained': self.get_proficiency_display_short(),
            'color': self.get_proficiency_color(),
            'how_learned': self.how_learned,
            'improvement': self.get_skill_improvement(),
            'date': self.created_at,
        }


class LearningMilestone(models.Model):
    """
    Track major learning milestones and achievements
    Focused on key moments in learning journey
    """

    MILESTONE_TYPES = (
        ('first_time', 'First Time Using Technology'),
        ('breakthrough', 'Major Understanding Breakthrough'),
        ('completion', 'Project Completion'),
        ('deployment', 'First Successful Deployment'),
        ('debugging', 'Major Problem Solved'),
        ('teaching', 'First Time Teaching/Helping Others'),
        ('contribution', 'Open Source Contribution'),
        ('recognition', 'External Recognition'),
    )

    # Core info
    system = models.ForeignKey(SystemModule, on_delete=models.CASCADE, related_name='milestones', help_text='Project/System this milestone is related to')
    milestone_type = models.CharField(max_length=20, choices=MILESTONE_TYPES, help_text='Type of learning milestone')
    title = models.CharField(max_length=200, help_text='Brief milestone title (e.g. "First successful API integration")')
    description = models.TextField(help_text="What you achieved and why it was significant")
    date_achieved = models.DateTimeField(help_text="When did you achieve this milestone?")

    # Optional Connections
    related_post = models.ForeignKey('blog.Post', on_delete=models.SET_NULL, null=True, blank=True, related_name='documented_milestones', help_text='DataLog entry about this milestone (optional)')
    related_skill = models.ForeignKey('core.Skill', on_delete=models.SET_NULL, null=True, blank=True, related_name='milestones', help_text='Primary skill this relates to (optional)')

    # Learning impact (simple 1-5 scale)
    difficulty_level = models.IntegerField(
        choices=[(i, f"Level {i}") for i in range(1, 6)],
        default=3,
        help_text="How challenging was this to achieve? (1=Easy, 5=Very Hard)"
    )

    confidence_boost = models.IntegerField(
        choices=[(i, f"{i} stars") for i in range(1, 6)],
        default=3,
        help_text="How much did this boost you confidence? (1-5 stars)"
    )

    # Sharing/Impact
    shared_publicly = models.BooleanField(default=False, help_text="Did you share this achievement? (blog, social media, etc)")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_achieved']
        verbose_name = "Learning Milestone"
        verbose_name_plural = "Learning Milestones"

    def __str__(self):
        return f"{self.title} - {self.system.title}"

    def get_milestone_icon(self):
        """Font Awesome icon for milestone type"""
        icons = {
            "first_time": "fas fa-star",
            "breakthrough": "fas fa-lightbulb",
            "completion": "fas fa-check-circle",
            "deployment": "fas fa-rocket",
            "debugging": "fas fa-bug",
            "teaching": "fas fa-chalkboard-teacher",
            "contribution": "fas fa-code-branch",
            "recognition": "fas fa-trophy",
        }
        return icons.get(self.milestone_type, "fas fa-star")

    def get_milestone_color(self):
        """Color for milestone type"""
        colors = {
            "first_time": "#FFD54F",  # Gold
            "breakthrough": "#4FC3F7",  # Cyan
            "completion": "#81C784",  # Green
            "deployment": "#64B5F6",  # Blue
            "debugging": "#FF8A65",  # Orange
            "teaching": "#A5D6A7",  # Light green
            "contribution": "#90CAF9",  # Light blue
            "recognition": "#FFB74D",  # Amber
        }
        return colors.get(self.milestone_type, "#64B5F6")

    def get_difficulty_stars(self):
        """Visual difficulty representation"""
        return "★" * self.difficulty_level + "☆" * (5 - self.difficulty_level)

    def get_confidence_stars(self):
        """Visual confidence boost representation"""
        return "★" * self.confidence_boost + "☆" * (5 - self.confidence_boost)

    def days_since_achieved(self):
        """Days since milestone was achieved"""
        return (timezone.now() - self.date_achieved).days

    def get_absolute_url(self):
        """Link to related content"""
        if self.related_post:
            return self.related_post.get_absolute_url()
        return self.system.get_absolute_url()

    def get_milestone_summary(self):
        """Summary for dashboard cards"""
        return {
            "title": self.title,
            "type": self.get_milestone_type_display(),
            "system": self.system.title,
            "date": self.date_achieved,
            "difficulty": self.difficulty_level,
            "confidence_boost": self.confidence_boost,
            "icon": self.get_milestone_icon(),
            "color": self.get_milestone_color(),
            "days_ago": self.days_since_achieved(),
            "has_post": bool(self.related_post),
            "shared": self.shared_publicly,
        }
