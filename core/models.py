from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from django.utils import timezone

from datetime import date
from projects.models import SystemSkillGain, Technology


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
        # Enhanced w mastery level
        mastery = self.get_mastery_level().title()
        system_count = self.get_systems_count()
        if system_count > 0:
            return f"{self.name} ({mastery} - {system_count} systems)"
        return f"{self.name} ({self.get_proficiency_percentage():.0f}%)"

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

    # ================= LEARNING-FOCUSED METHODS =================

    def get_learning_progression(self):
        """
        Get learning progression of this skill across projects/systems
        Shows how skill is developed over time
        """
        gains = SystemSkillGain.objects.filter(
            skill=self
        ).select_related('system').order_by('system__created_at')

        progression = []
        for gain in gains:
            progression.append({
                'system': gain.system.title,
                'system_slug': gain.system.slug,
                'date': gain.system.created_at,
                'proficiency_gained': gain.proficiency_gained,
                'proficiency_display': gain.get_proficiency_display_short(),
                'how_learned': gain.how_learned,
                'learning_stage': gain.system.get_learning_stage_display(),
                'color': gain.get_proficiency_color(),
            })
        return progression

    def get_systems_using_skill(self):
        """Get all systems where this skill was developed/used"""
        return SystemSkillGain.objects.filter(skill=self).select_related('system').order_by('-system__created_at')

    def get_systems_count(self):
        """Get count of systems using this skill"""
        return self.get_systems_using_skill().count()

    def get_latest_usage(self):
        """Get the most recent system that used this skill"""
        latest = self.get_systems_using_skill().first()
        return latest.system if latest else None

    def get_first_usage(self):
        """Get the first system that used this skill"""
        first = self.get_systems_using_skill().last()
        return first.system if first else None

    def get_skill_milestones(self):
        """Get learning milestones related to this skill"""
        return self.milestones.select_related('system').order_by('-date_achieved')

    def get_mastery_level(self):
        """
        Calculate mastery level based on project usage and proficiency
        Returns: beginner, intermediate, advanced, expert
        """
        system_count = self.get_systems_count()
        current_proficiency = self.proficiency

        # Mastery based on both usage frequency and proficiency level
        if system_count >= 5 and current_proficiency >= 4:
            return 'expert'
        elif system_count >= 3 and current_proficiency >= 3:
            return 'advanced'
        elif system_count >= 2 and current_proficiency >= 2:
            return 'intermediate'
        else:
            return 'beginner'

    def get_mastery_color(self):
        """Get color for mastery level"""
        mastery = self.get_mastery_level()
        colors = {
            "beginner": "#FFB74D",  # Orange
            "intermediate": "#81C784",  # Green
            "advanced": "#64B5F6",  # Blue
            "expert": "#FFD54F",  # Gold
        }
        return colors.get(mastery, "#81C784")

    def get_learning_velocity(self):
        """
        Calculate how quickly this skill was developed
        Projects/Systems using this skill per month
        """
        first_system = self.get_first_usage()
        latest_system = self.get_latest_usage()

        if not (first_system and latest_system):
            return 0

        # Calculate months between first and latest usage
        time_diff = latest_system.created_at - first_system.created_at
        months = max(time_diff.days / 30, 1)

        # Systems using this skill
        system_count = self.get_systems_count()

        return round(system_count / months, 2)

    def get_total_learning_time_estimate(self):
        """
        Estimate total time spent learning this skill across projects
        Based on actual_dev_hours in projects that used this skill
        """
        total_hours = 0

        for system_gain in self.get_systems_using_skill():
            system = system_gain.system
            if system.actual_dev_hours:
                # Assume skill was used for portion of project time
                # based on how many technologies were in the project
                tech_count = system.technologies.count()
                skill_portion = 1 / max(tech_count, 1)  # Divide time among technologies
                total_hours += system.actual_dev_hours * skill_portion
            elif system.estimated_dev_hours:
                # Fallback to estimated hours
                tech_count = system.technologies.count()
                skill_portion = 1 / max(tech_count, 1)
                total_hours += system.estimated_dev_hours * skill_portion

        return round(total_hours, 1)

    def has_breakthroughs(self):
        """Check if any systems/projects has breakthrough moments with this skill"""
        return self.get_systems_using_skill().exclude(how_learned__exact='').exists()

    def get_breakthrough_moments(self):
        """Get all breakthrough moments related to this skill"""
        breakthroughs = []

        for system_gain in self.get_systems_using_skill():
            if system_gain.how_learned:
                breakthroughs.append({
                    'system': system_gain.system.title,
                    'learning_story': system_gain.how_learned,
                    'date': system_gain.system.created_at,
                    'proficiency_gained': system_gain.get_proficiency_display_short(),
                })
        return breakthroughs

    def get_related_technologies(self):
        """
        Get technologies that were used alongside this skill
        Shows what this skill is commonly paired with
        """
        # Get all systems that used this skill
        systems_with_skill = [
            system_gain.system for system_gain in self.get_systems_using_skill()
        ]

        # Get technologies used in those systems
        related_techs = Technology.objects.filter(
            systems__in=systems_with_skill
        ).distinct().exclude(name=self.name)  # Exclude self if skill name matches tech name

        return related_techs

    def get_skill_summary_for_dashboard(self):
        """Get comprehensive skill summary for dashboard display"""
        return {
            'name': self.name,
            'category': self.get_category_display(),
            'proficiency': self.proficiency,
            'proficiency_percentage': self.get_proficiency_percentage(),
            'mastery_level': self.get_mastery_level(),
            'mastery_color': self.get_mastery_color(),
            'systems_count': self.get_systems_count(),
            'learning_velocity': self.get_learning_velocity(),
            'total_time_estimate': self.get_total_learning_time_estimate(),
            'has_milestones': self.get_skill_milestones().exists(),
            'is_featured': self.is_featured,
            'is_currently_learning': self.is_currently_learning,
            'years_experience': self.years_experience,
            'color': self.color,
            'icon': self.icon,
        }

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
