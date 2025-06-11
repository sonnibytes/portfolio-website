from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from django.utils import timezone

from datetime import date


class CorePage(models.Model):
    """Model for static pages like privacy policy, etc."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    content = MarkdownxField()
    meta_description = models.CharField(
        max_length=160,
        help_text="SEO meta description")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:page", args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def rendered_content(self):
        """Return content as rendered HTML."""
        return markdownify(self.content)


class Skill(models.Model):
    """Dev skills with proficiency values for visualization."""

    CATEGORY_CHOICES = (
        ("languages", "Programming Languages"),
        ("frameworks", "Frameworks & Libraries"),
        ("tools", "Tools & Technologies"),
        ("databases", "Databases"),
        ("other", "Other Skills"),
    )

    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    proficiency = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)],
        help_text="Skill level from 1-5"
    )
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon name (e.g., fa-python)")
    color = models.CharField(max_length=7, default="#00f0ff", help_text="Hex color code")
    display_order = models.PositiveIntegerField(default=0)

    # Technology Relationship
    related_technology = models.OneToOneField('projects.Technology', on_delete=models.SET_NULL, null=True, blank=True, related_name='skill_profile', help_text="Link to corresponding technology in projects app")

    # Experience Tracking
    years_experience = models.FloatField(default=0.0, help_text="Years of experience with this skill")

    # Featured Status
    is_featured = models.BooleanField(default=False, help_text="Display prominently on homepage")

    # Recency Tracking
    last_used = models.DateField(null=True, blank=True, help_text="When skill last used professionally")

    # Learning Status
    is_currently_learning = models.BooleanField(default=False, help_text="Currently improving this skill")

    # Skill Validation
    is_certified = models.BooleanField(default=False, help_text="Have certification in this skill")

    class Meta:
        ordering = ['category', 'display_order']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("core:skill", args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_experience_level(self):
        """Return experiience level based on years"""
        if self.years_experience >= 5:
            return "Expert"
        elif self.years_experience >= 3:
            return "Advanced"
        elif self.years_experience >= 1:
            return "Intermediate"
        else:
            return "Beginner"

    def is_recent(self):
        """Check if skill was used recently (within 2 years)"""
        if not self.last_used:
            # Assume recent if no set date
            return True
        years_since = (date.today() - self.last_used).days / 365
        return years_since <= 2

    def get_proficiency_percentage(self):
        """Convert 1-5 scale to percentage"""
        return (self.proficiency / 5) * 100


class Education(models.Model):
    """Educational background."""

    institution = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=200)
    degree = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ["-end_date", "-start_date"]
        verbose_name_plural = "Education"

    def __str__(self):
        return f"{self.degree} from {self.institution}"

    def get_absolute_url(self):
        return reverse("core:education", args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Experience(models.Model):
    """Work experience."""

    company = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=200)
    position = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    technologies = models.CharField(max_length=200, blank=True, help_text="Comma-separated list of technologies used")

    class Meta:
        ordering = ["-end_date", "-start_date"]

    def __str__(self):
        return f"{self.position} at {self.company}"

    def get_absolute_url(self):
        return reverse("core:experience", args=[self.slug])

    def get_technologies_list(self):
        """Return technologies as a list."""
        if self.technologies:
            return [tech.strip() for tech in self.technologies.split(",")]
        return []

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Contact(models.Model):
    """Model for contact form submissions."""

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    # Tracking Metadata
    referrer_page = models.CharField(max_length=200, blank=True, help_text="Page the visitor came from")
    user_agent = models.TextField(blank=True, help_text="Browser/device info")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="Visitor IP address")

    # Response Tracking
    response_sent = models.BooleanField(default=False, help_text="Has response been sent")
    response_date = models.DateTimeField(null=True, blank=True, help_text="When response was sent")

    # Categorization
    inquiry_category = models.CharField(
        max_length=50,
        choices=[
            ('project', 'Project Inquiry'),
            ('hiring', 'Job/Hiring'),
            ('collaboration', 'Collaboration'),
            ('question', 'General Question'),
            ('feedback', 'Feedback'),
            ('other', 'Other'),
        ],
        default='other'
    )

    # Priority level
    priority = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low Priority'),
            ('normal', 'Normal Priority'),
            ('high', 'High Priority'),
            ('urgent', 'Urgent'),
        ],
        default='normal'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.name} - {self.created_at.strftime('%Y-%m-%d')}"

    def get_absolute_url(self):
        return reverse("core:contact_detail", args=[self.pk])

    def response_time_hours(self):
        """Calculate hours between submission and response"""
        if self.response_date and self.created_at:
            delta = self.response_date = self.created_at
            return delta.total_seconds() / 3600
        return None

    def mark_as_responded(self):
        """Mark contact as responded to"""
        self.response_sent = True
        self.response_date = timezone.now()
        self.save()


class SocialLink(models.Model):
    """Model for social media and external profile links."""

    name = models.CharField(max_length=50)
    url = models.URLField()
    handle = models.CharField(max_length=100, blank=True)
    icon = models.CharField(
        max_length=50, blank=True, help_text="Font Awesome icon name (e.g., 'fa-github')"
    )
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return self.url  # External URL, so just return the actual URL


class PortfolioAnalytics(models.Model):
    """Daily portfolio performance and visitor analytics."""
    # Date tracking
    date = models.DateField(unique=True)

    # Visitor metrics
    unique_visitors = models.IntegerField(default=0)
    page_views = models.IntegerField(default=0)
    bounce_rate = models.FloatField(default=0.0, help_text="Percentage of single-page sessions")
    avg_session_duration = models.IntegerField(default=0, help_text="Average session duration in seconds")

    # Content engagement metrics
    datalog_views = models.IntegerField(default=0)
    system_views = models.IntegerField(default=0)
    contact_form_submissions = models.IntegerField(default=0)
    github_clicks = models.IntegerField(default=0)

    # Top performing content
    top_datalog = models.ForeignKey('blog.Post', null=True, blank=True, on_delete=models.SET_NULL, related_name='analytics_days_as_top')
    top_system = models.ForeignKey('projects.SystemModule', null=True, blank=True, on_delete=models.SET_NULL, related_name='analytics_days_as_top')

    # Geographic Data
    top_country = models.CharField(max_length=50, blank=True)
    top_city = models.CharField(max_length=50, blank=True)

    # Referrer Data
    top_referrer = models.CharField(max_length=200, blank=True)
    organic_search_percentage = models.FloatField(default=0.0)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Portfolio Analytics"

    def __str__(self):
        return f"Analytics for {self.date} ({self.unique_visitors} visitors)"

    def get_absolute_url(self):
        return reverse("core:analytics_detail", args=[self.date])

    def conversion_rate(self):
        """Calculate contact form conversion rate"""
        if self.unique_visitors > 0:
            return (self.contact_form_submissions / self.unique_visitors) * 100
        return 0.0

    def engagement_score(self):
        """Calculate overall engagement score"""
        base_score = 0
        if self.bounce_rate < 50:
            base_score += 25
        if self.avg_session_duration > 120:  # 2 minutes
            base_score += 25
        if self.datalog_views > self.page_views * 0.3:
            base_score += 25
        if self.contact_form_submissions > 0:
            base_score += 25
        return base_score
