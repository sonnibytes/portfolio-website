from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
import re
import calendar
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
from collections import defaultdict
from django.db.models import Avg, Count, Sum, Q
from django.utils import timezone


"""
ENHANCED SYSTEM ARCHITECTURE MODELS
System Type > System Module > System Features/Images
Connected to Blog via SystemLogEntry
"""

class GitHubCommitWeek(models.Model):
    """
    Weekly commit tracking for detailed analysis.
    Only populated for repos linked to systems.
    """
    repository = models.ForeignKey('GitHubRepository', on_delete=models.CASCADE, related_name='commit_weeks')

    # Week identification (using iso week)
    year = models.IntegerField(help_text="ISO year (YYYY)")
    week = models.IntegerField(help_text="ISO week number (1-53)")

    # Month metadata for easier querying and aggregation
    month = models.IntegerField(help_text="Month Number (1-2) of week start date")
    month_name = models.CharField(max_length=10, help_text="Month Name (e.g. January)")
    quarter = models.IntegerField(help_text="Quarter (1-4) for reporting")

    # Week metadata for easier querying
    week_start_date = models.DateField(help_text="Monday of this week")
    week_end_date = models.DateField(help_text="Sunday of this week")

    # Commit data
    commit_count = models.IntegerField(default=0, help_text="Commits in this week")

    # Optional detailed data (if we want to include)
    lines_added = models.IntegerField(default=0, blank=True)
    lines_deleted = models.IntegerField(default=0, blank=True)
    files_changed = models.IntegerField(default=0, blank=True)

    # Sync metadata
    last_synced = models.DateTimeField(auto_now=True)
    github_etag = models.CharField(max_length=64, blank=True, help_text="ETag for conditional requests")

    class Meta:
        unique_together = ['repository', 'year', 'week']
        ordering = ['-year', '-week']
        indexes = [
            models.Index(fields=['repository', 'year', 'week']),
            # Monthly queries
            models.Index(fields=['repository', 'year', 'month']),
            # Quarterly queries
            models.Index(fields=['repository', 'quarter', 'year']),
            models.Index(fields=['week_start_date']),
            # Cross repo monthly analysis
            models.Index(fields=['month', 'year']),
        ]
    
    def __str__(self):
        return f"{self.repository.name} - {self.year}W{self.week:02d} ({self.commit_count} commits)"
    
    @classmethod
    def get_iso_week_dates(cls, year, week):
        """Get start and end dates for an ISO week."""
        # January 4th is always in week 1
        jan4 = datetime(year, 1, 4)
        week_start = jan4 - timedelta(days=jan4.weekday()) + timedelta(weeks=week - 1)
        week_end = week_start + timedelta(days=6)
        return week_start.date(), week_end.date()
    
    @classmethod
    def create_from_iso_week(cls, repository, year, week, commit_count, **kwargs):
        """Create a commit week entry from ISO year/week with month metadata."""
        start_date, end_date = cls.get_iso_week_dates(year, week)

        # Calculate month metadata based on week start date (Monday)
        month = start_date.month
        month_name = start_date.strftime('%B')
        quarter = (month - 1) // 3 + 1

        return cls.objects.create(
            repository=repository,
            year=year,
            week=week,
            month=month,
            month_name=month_name,
            quarter=quarter,
            week_start_date=start_date,
            week_end_date=end_date,
            commit_count=commit_count,
            **kwargs
        )
    
    @property
    def is_current_week(self):
        """Check if this is the current week."""
        now = datetime.now()
        current_year, current_week, _ = now.isocalendar()
        return self.year == current_year and self.week == current_week
    
    def get_week_label(self):
        """Get human-readable week label."""
        if self.is_current_week:
            return "This week"
        
        # Check if it's recent
        now = datetime.now()
        week_start = self.week_start_date
        days_ago = (now.date() - week_start).days

        if days_ago <= 7:
            return "Last week"
        elif days_ago <= 14:
            return "2 weeks ago"
        elif days_ago <= 30:
            weeks_ago = days_ago // 7
            return f"{weeks_ago} weeks ago"
        else:
            return f"{week_start.strftime('%b %d, %Y')}"
    
    def get_month_label(self):
        """Get human-readable month label for this week."""
        return f"{self.month_name} {self.year}"
    
    @classmethod
    def get_monthly_summary(cls, repository, year, month):
        """Get commit summary for a specific month."""
        weeks_in_month = cls.objects.filter(repository=repository, year=year, month=month)

        if not weeks_in_month:
            return {
                'month': month,
                'month_name': '',
                'total_commits': 0,
                'weeks_count': 0,
                'avg_commits_per_week': 0
            }
        
        total_commits = sum(week.commit_count for week in weeks_in_month)
        weeks_count = weeks_in_month.count()

        return {
            'month': month,
            'month_name': weeks_in_month.first().month_name,
            'year': year,
            'total_commits': total_commits,
            'weeks_count': weeks_count,
            'avg_commits_per_week': round(total_commits / weeks_count, 1) if weeks_count > 0 else 0,
            'most_active_week': max(weeks_in_month, key=lambda w: w.commit_count) if weeks_in_month else None
        }
    
    @classmethod
    def get_quarterly_summary(cls, repository, year, quarter):
        """Get commit summary for a specific quarter."""
        weeks_in_quarter = cls.objects.filter(repository=repository, year=year, quarter=quarter)

        if not weeks_in_quarter:
            return {
                'quarter': quarter,
                'year': year,
                'total_commits': 0,
                'weeks_count': 0,
                'months_included': []
            }
        
        total_commits = sum(week.commit_count for week in weeks_in_quarter)
        months_in_quarter = list(set(week.month for week in weeks_in_quarter))

        return {
            'quarter': quarter,
            'year': year,
            'total_commits': total_commits,
            'weeks_count': weeks_in_quarter.count(),
            'months_included': sorted(months_in_quarter),
            'avg_commits_per_week': round(total_commits / weeks_in_quarter.count(), 1) if weeks_in_quarter else 0
        }


# Enhanced GitHubRepository model methods
class GitHubRepositoryManager(models.Manager):
    def with_detailed_tracking(self):
        """Get repositories that have detailed weekly commit tracking."""
        return self.filter(related_system__isnull=False, is_archived=False, is_fork=False)
    
    def needs_weekly_sync(self, hours_threshold=24):
        """Get repos that week weekly commit data sync."""
        cutoff = timezone.now() - timedelta(hours=hours_threshold)
        return self.with_detailed_tracking().filter(
            Q(commit_weeks_last_synced__isnull=True) | Q(commit_weeks_last_synced__lt=cutoff)
        )


class GitHubRepository(models.Model):
    """Model to store GitHub repository data locally with enhanced commit tracking."""

    # Basic repo info
    github_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    # URLs and Links
    html_url = models.URLField()
    clone_url = models.URLField()
    homepage = models.URLField(blank=True, null=True)

    # Repository stats
    stars_count = models.IntegerField(default=0)
    forks_count = models.IntegerField(default=0)
    watchers_count = models.IntegerField(default=0)
    size = models.IntegerField(default=0)  # size in KB

    # Repository metadata
    language = models.CharField(max_length=50, blank=True, null=True)
    is_private = models.BooleanField(default=False)
    is_fork = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)

    # Timestamps
    github_created_at = models.DateTimeField()
    github_updated_at = models.DateTimeField()
    last_synced = models.DateTimeField(auto_now=True)

    # Integration w existing SystemModule
    related_system = models.ForeignKey('SystemModule', on_delete=models.SET_NULL, null=True, blank=True, related_name='github_repositories')

    # ===== EXISTING COMMIT SUMMARY FIELDS (KEEP - SERVE DIFFERENT PURPOSE) =====
    # These provide quick stats without needing to aggregate weekly data
    total_commits = models.IntegerField(default=0, help_text='Total commits in repository')
    last_commit_date = models.DateTimeField(null=True, blank=True, help_text='Date of most recent commit')
    last_commit_sha = models.CharField(max_length=40, blank=True, help_text='SHA of most recent commit')
    last_commit_message = models.TextField(blank=True, help_text='Message of the most recent commit')

    # Commit activity metrics (Quick overview stats)
    commits_last_30_days = models.IntegerField(default=0, help_text="Commits in last 30 days")
    commits_last_year = models.IntegerField(default=0, help_text="Commits in last year")
    avg_commits_per_month = models.FloatField(default=0.0, help_text="Average commits per month")
    
    # Commit Overview sync metadata
    commits_last_synced = models.DateTimeField(null=True, blank=True, help_text="When commit data was last synced")
    commit_sync_page = models.IntegerField(default=1, help_text="Last synced page for pagination")

    # ===== NEW WEEKLY TRACKING FIELDS (ADD THESE) =====
    # Enhanced tracking for system-linked repositories
    commit_weeks_last_synced = models.DateTimeField(null=True, blank=True, help_text="When weekly commit data last synced")

    # ETag for GitHub stattistic endpoint (conditional requests)
    stats_etag = models.CharField(max_length=64, blank=True, help_text="ETag for GitHub stats API conditional requests")

    # Flag to enable detailed tracking (auto-enabled for system-linked repos)
    enable_detailed_tracking = models.BooleanField(default=False, help_text="Enable weekly commit tracking (auto-enabled for system-linked repos)")

    # ===== CUSTOM MANAGER =====
    objects = GitHubRepositoryManager()

    class Meta:
        ordering = ['-github_updated_at']
        verbose_name = 'GitHub Repository'
        verbose_name_plural = 'GitHub Repositories'
    
    def __str__(self):
        return self.full_name
    
    @property
    def is_recently_active(self):
        """Check if repo was updated in last 30 days."""
        return self.github_updated_at >= timezone.now() - timedelta(days=30)

    @property
    def is_commit_active(self):
        """Check if repo had commits in last 30 days."""
        return self.commits_last_30_days > 0
    
    @property
    def commit_frequency_rating(self):
        """Get a rating for commit frequency (1-5 scale)."""
        if self.commits_last_30_days >= 20:
            return 5  # Very active
        elif self.commits_last_30_days >= 10:
            return 4  # Active
        elif self.commits_last_30_days >= 5:
            return 3  # Moderate
        elif self.commits_last_30_days >= 1:
            return 2  # Low
        else:
            return 1  # Inactive
    
    @property
    def days_since_last_commit(self):
        """Calculate days since last commit."""
        if not self.last_commit_date:
            return None
        return (timezone.now() - self.last_commit_date).days
    
    def get_commit_summary(self):
        """Get human-readable commit summary."""
        if not self.last_commit_date:
            return "No commits tracked"
        
        days_ago = self.days_since_last_commit

        if days_ago == 0:
            last_commit = 'today'
        elif days_ago == 1:
            last_commit = 'yesterday'
        elif days_ago < 7:
            last_commit = f'{days_ago} days ago'
        elif days_ago < 30:
            weeks = days_ago // 7
            last_commit = f'{weeks} week{"s" if weeks > 1 else ""} ago'
        else:
            months = days_ago // 30
            last_commit = f"{months} month{'s' if months > 1 else ''} ago"
        
        return f"{self.total_commits} commits, last {last_commit}"
    
    # ===== NEW ENHANCED METHODS (Added w Weekly Commit model) =====
    def should_track_detailed_commits(self):
        """Determine if this repo should have detailed weekly tracking."""
        return (
            self.related_system is not None and
            not self.is_archived and
            not self.is_fork
        )
    
    def get_weekly_commit_data(self, weeks_back=12):
        """Get weekly commit data for last N weeks."""
        return self.commit_weeks.order_by('-year', '-week')[:weeks_back]
    
    def get_monthly_commit_data(self, months_back=6):
        """Get monthly commit summaries for the last N months."""
        # Get all weeks from the last N months
        recent_weeks = self.commit_weeks.order_by('-year', '-month', '-week')

        # Group by year-month
        monthly_data = defaultdict(list)
        for week in recent_weeks:
            month_key = f"{week.year}-{week.month:02d}"
            monthly_data[month_key].append(week)
        
        # Convert to monthly summaries
        monthly_summaries = []
        for month_key in sorted(monthly_data.keys(), reverse=True)[:months_back]:
            weeks = monthly_data[month_key]
            if weeks:
                total_commits = sum(w.commit_count for w in weeks)
                first_week = weeks[0]  # For month metadata

                monthly_summaries.append({
                    'year': first_week.year,
                    'month': first_week.month,
                    'month_name': first_week.month_name,
                    'total_commits': total_commits,
                    'week_count': len(weeks),
                    'avg_commits_per_week': round(total_commits / len(weeks), 1),
                    'most_active_week': max(weeks, key=lambda w: w.commit_count)
                })
        
        return monthly_summaries
    
    def get_commit_trend(self, weeks=4):
        """Get commit trend over recent weeks."""
        recent_weeks = self.commit_weeks.order_by('-year', '-week')[:weeks]
        if not recent_weeks:
            return "no-data"
        
        commits = [w.commit_count for w in recent_weeks]
        if len(commits) < 2:
            return "Insufficient-data"
        
        # Simple trend calculation
        first_half = sum(commits[:len(commits) // 2])
        second_half = sum(commits[len(commits) // 2:])

        if second_half > first_half * 1.2:
            return "increasing"
        elif second_half < first_half * 0.8:
            return "decreasing"
        else:
            return "stable"
    
    def get_monthly_trend(self, months=3):
        """Get commit trend over recent months."""
        monthly_data = self.get_monthly_commit_data(months_back=months)
        if len(monthly_data) < 2:
            return "Insufficient-data"
        
        # Compare first half to second half of months
        commits = [month['total_commits'] for month in monthly_data]
        first_half = sum(commits[:len(commits) // 2])
        second_half = sum(commits[len(commits) // 2:])

        if second_half > first_half * 1.3:
            return "increasing"
        elif second_half < first_half * 0.7:
            return "decreasing"
        else:
            return "stable"
    
    def get_weekly_commit_summary(self):
        """Get a summary of weekly commit activity."""
        weeks = self.commit_weeks.all()
        if not weeks:
            return {
                'total_weeks': 0,
                'avg_commits_per_week': 0,
                'most_active_week': None,
                'recent_activity': 'No data'
            }
        
        total_commits = sum(w.commit_count for w in weeks)
        most_active = max(weeks, key=lambda w: w.commit_count)

        return {
            'total_weeks': weeks.count(),
            'avg_commits_per_week': round(total_commits / weeks.count(), 1),
            'most_active_week': most_active,
            'trend': self.get_commit_trend(),
            'total_commits_tracked': total_commits
        }
    
    def get_monthly_commit_summary(self):
        """Get a summary of monthly commit activity."""
        monthly_data = self.get_monthly_commit_data(months_back=12)
        if not monthly_data:
            return {
                'total_months': 0,
                'avg_commits_per_month': 0,
                'most_active_month': None,
                'monthly_trend': 'no-data'
            }
        
        total_commits = sum(month['total_commits'] for month in monthly_data)
        most_active = max(monthly_data, key=lambda m: m['total_commits'])

        return {
            'total_months': len(monthly_data),
            'avg_commits_per_month': round(total_commits / len(monthly_data), 1),
            'most_active_month': most_active,
            'monthly_trend': self.get_monthly_trend(),
            'total_commits_tracked': total_commits
        }
    
    def update_summary_from_weekly_data(self):
        """
        Update basic commit summary fields using accurate weekly data.
        Call this after weekly sync to get real numbers instead of estimates.
        """
        if not self.enable_detailed_tracking:
            return False
        
        # Get all weekly commit data for this repo
        weekly_data = self.commit_weeks.all()
        
        if not weekly_data:
            return False
        
        # Calculate accurate total commits from weekly data
        total_commits = sum(week.commit_count for week in weekly_data)
        
        # Calculate commits in last 30 days (approximately last 4-5 weeks)
        recent_weeks = weekly_data.order_by('-year', '-week')[:5]  # Last 5 weeks to cover 30+ days
        commits_last_30_days = sum(week.commit_count for week in recent_weeks)
        
        # Calculate commits in last year (all our data since we only store 52 weeks max)
        commits_last_year = total_commits
        
        # Calculate average commits per month from weekly data
        weeks_count = weekly_data.count()
        if weeks_count > 0:
            avg_commits_per_week = total_commits / weeks_count
            avg_commits_per_month = avg_commits_per_week * 4.33  # Average weeks per month
        else:
            avg_commits_per_month = 0.0
        
        # Update the summary fields with accurate data
        self.total_commits = total_commits
        self.commits_last_30_days = commits_last_30_days
        self.commits_last_year = commits_last_year
        self.avg_commits_per_month = round(avg_commits_per_month, 2)
        
        # Save the updated summary
        self.save(update_fields=[
            'total_commits', 
            'commits_last_30_days', 
            'commits_last_year', 
            'avg_commits_per_month'
        ])
        
        return True

    def get_accurate_vs_estimated_comparison(self):
        """
        Compare estimated vs accurate commit data for debugging.
        Useful to see how far off the estimates were.
        """
        if not self.enable_detailed_tracking:
            return None
        
        # Store current (estimated) values
        estimated_total = self.total_commits
        estimated_30_days = self.commits_last_30_days
        
        # Calculate accurate values from weekly data
        weekly_data = self.commit_weeks.all()
        if not weekly_data:
            return None
        
        accurate_total = sum(week.commit_count for week in weekly_data)
        recent_weeks = weekly_data.order_by('-year', '-week')[:5]
        accurate_30_days = sum(week.commit_count for week in recent_weeks)
        
        return {
            'estimated': {
                'total': estimated_total,
                'last_30_days': estimated_30_days
            },
            'accurate': {
                'total': accurate_total,
                'last_30_days': accurate_30_days
            },
            'difference': {
                'total': accurate_total - estimated_total,
                'last_30_days': accurate_30_days - estimated_30_days
            }
        }


class GitHubLanguage(models.Model):
    """Model to store programming language usage across repositories."""
    # TODO: Change language to link to technologies that are languages - 
    # TODO: actually will need to use a junction model to link so commands can update w api data w/o affecting tech entries

    repository = models.ForeignKey(GitHubRepository, on_delete=models.CASCADE, related_name='languages')
    language = models.CharField(max_length=50)
    bytes_count = models.BigIntegerField()
    percentage = models.FloatField()  # Percentage of total repo size

    class Meta:
        unique_together = ['repository', 'language']
        ordering = ['-bytes_count']
    
    def __str__(self):
        return f"{self.repository.name} - {self.language} ({self.percentage:.1f}%)"


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
        # Added os and AI/ML since there are enough of them to be their own category
        ('os', 'Operating Systems & Distros'),
        ('ai', 'AI & Machine Learning'),
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
    # Formerly features_overview
    usage_examples = MarkdownxField(
        blank=True, help_text="Usage examples and key features"
    )
    # Formerly technical_details
    setup_instructions = MarkdownxField(
        blank=True,
        help_text="Setup instructions and implementation details"
    )
    # TODO: May remove? Redundant and just another field to complete. Can address challenges w related DataLogs
    # Keep this short, problem system solved, with solution as approach in a nutshell
    challenges = MarkdownxField(
        blank=True,
        help_text="Development challenge this system solved, and solution/approach"
    )
    # # lean on connected features w implementation status of 'planned' or 'in progress'
    # future_enhancements = MarkdownxField(
    #     blank=True,
    #     help_text="Planned improvement and next steps"
    # )

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
    # TODO: May remove demo_url and use live_url for both?
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
    # architecture_diagram = models.ImageField(
    #     upload_to="systems/diagrams/",
    #     null=True,
    #     blank=True,
    #     help_text="System architecture diagram",
    # )

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

    def render_usage_examples(self):
        """Return usage examples as HTML."""
        return markdownify(self.usage_examples)
    
    def rendered_setup_instructions(self):
        """Return setup instructions field as HTML."""
        return markdownify(self.setup_instructions)

    def rendered_challenges(self):
        """Return challenges field as HTML."""
        return markdownify(self.challenges)

    # def rendered_future_enhancements(self):
    #     """Return future enhancements field as HTML."""
    #     return markdownify(self.future_enhancements)

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
        """Get all related system logs ordered by relationship priority and date"""
        return (
            self.log_entries.all()
            .select_related("post")
            .order_by("-relationship_priority", "-created_at")
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
        commit_stats = self.get_commit_stats()

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
                # Updated to use GitHub data
                'commit_count': commit_stats['total_commits'],
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
        if self.usage_examples:
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
        """Learning-focused stats using existing fields w github data enhancements"""
        commit_stats = self.get_commit_stats()

        return {
            # Use existing time tracking
            'estimated_hours': self.estimated_dev_hours or 0,
            'actual_hours': self.actual_dev_hours or 0,
            'hours_variance': self.hours_variance() or 0,

            # Use existing code metrics
            'lines_of_code': self.code_lines,
            # Updating to use GitHub data
            'commits': commit_stats['total_commits'],
            'last_commit': commit_stats['last_commit_date'],
            'commits_30_days': commit_stats['commits_last_30_days'],
            'commits_year': commit_stats['commits_last_year'],
            'repository_count': commit_stats['repository_count'],
            'active_repo_count': commit_stats['active_repo_count'],
            'avg_commits_per_month': commit_stats['avg_commits_per_month'],
            'most_active_repo': commit_stats['most_active_repo'],
            'commit_frequency_rating': commit_stats['commit_frequency_rating'],

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
        """GitHub activity summary using existing fields *Updated w GH Data"""
        commit_stats = self.get_commit_stats()
        return {
            'repository_url': self.github_url,
            # Updated to use GH data
            'commits': commit_stats['total_commits'],
            'lines_of_code': self.code_lines,
            'last_activity': commit_stats['last_commit_date'],
            'has_repo': bool(self.github_url),
            'active_development': commit_stats['commits_last_30_days'] > 0,
        }
    
    # Additional Learning Enhancements
    def get_learning_impact_score(self):
        # Calculate the learning impact of this system
        score = 0
        
        # Skills gained weight
        skills_count = self.skills_developed.count()
        score += min(40, skills_count * 8)
        
        # Complexity and learning stage
        if self.learning_stage in ['independent', 'refactoring', 'teaching']:
            score += 20
        elif self.learning_stage in ['guided']:
            score += 10
        
        # Portfolio readiness
        if self.portfolio_ready:
            score += 20
        
        # Milestones achieved
        milestones_count = self.milestones.count()
        score += min(20, milestones_count * 5)
        
        return min(100, score)

    def get_skill_development_summary(self):
        # Get summary of skill development from this system
        skill_gains = self.skill_gains.all()
        
        return {
            'total_skills': skill_gains.count(),
            'new_skills': skill_gains.filter(proficiency_gained=1).count(),
            'improved_skills': skill_gains.filter(proficiency_gained__gte=2).count(),
            'mastered_skills': skill_gains.filter(proficiency_gained__gte=4).count(),
            'skill_categories': skill_gains.values_list(
                'skill__category', flat=True
            ).distinct().count(),
            'learning_breakthroughs': skill_gains.filter(
                how_learned__isnull=False
            ).exclude(how_learned='').count(),
        }

    def get_learning_recommendations(self):
        # Get recommendations for improving learning value
        recommendations = []
        
        if not self.portfolio_ready and self.completion_percent >= 80:
            recommendations.append({
                'type': 'portfolio_ready',
                'title': 'Consider marking as portfolio-ready',
                'description': 'This system is nearly complete and could showcase your skills',
                'priority': 'high',
            })
        
        if self.skills_developed.count() < 2:
            recommendations.append({
                'type': 'skill_tracking',
                'title': 'Add skill connections',
                'description': 'Document what skills you developed or improved',
                'priority': 'medium',
            })
        
        if not self.milestones.exists():
            recommendations.append({
                'type': 'milestone_tracking',
                'title': 'Add learning milestones',
                'description': 'Document breakthrough moments and achievements',
                'priority': 'medium',
            })
        
        return recommendations
    
    # ================= Commit stats from GitHubRepository Data =================

    def get_commit_stats(self):
        """Get aggregated commit stats from related GitHub repositories."""
        repos = self.github_repositories.all()

        if not repos.exists():
            return {
                'total_commits': 0,
                'last_commit_date': None,
                'commits_last_30_days': 0,
                'commits_last_year': 0,
                'repository_count': 0,
                'avg_commits_per_month': 0,
                'active_repo_count': 0,
                'most_active_repo': None,
                'commit_frequency_rating': 1
            }
        
        # Aggregate commit data
        total_commits = repos.aggregate(Sum('total_commits'))['total_commits__sum'] or 0
        commits_30_days = repos.aggregate(Sum('commits_last_30_days'))['commits_last_30_days__sum'] or 0
        commits_year = repos.aggregate(Sum('commits_last_year'))['commits_last_year__sum'] or 0

        # Find most recent commit across all repos
        most_recent_repo = repos.filter(last_commit_date__isnull=False).order_by('-last_commit_date').first()
        last_commit_date = most_recent_repo.last_commit_date if most_recent_repo else None

        # Find most active repo
        most_active_repo = repos.order_by('-commits_last_30_days').first()

        # Count active repositories
        active_repo_count = repos.filter(commits_last_30_days__gt=0).count()

        # Calculate avg commits per month across all repos
        avg_commits = repos.aggregate(Avg('avg_commits_per_month'))['avg_commits_per_month__avg'] or 0.0

        # Calculate overall activity rating
        if commits_30_days >= 50:
            frequency_rating = 5
        elif commits_30_days >= 25:
            frequency_rating = 4
        elif commits_30_days >= 10:
            frequency_rating = 3
        elif commits_30_days >= 1:
            frequency_rating = 2
        else:
            frequency_rating = 1
        
        return {
            'total_commits': total_commits,
            'last_commit_date': last_commit_date,
            'commits_last_30_days': commits_30_days,
            'commits_last_year': commits_year,
            'repository_count': repos.count(),
            'active_repo_count': active_repo_count,
            'avg_commits_per_month': round(avg_commits, 1),
            'most_active_repo': most_active_repo,
            'commit_frequency_rating': frequency_rating
        }
    
    def get_development_timeline(self):
        """Get development timeline data for charts/graphs."""
        repos = self.github_repositories.all()

        # This could be expanded to create monthly/weekly commit data
        # For now, return basic timeline info
        timeline_data = []

        for repo in repos:
            if repo.last_commit_date:
                timeline_data.append({
                    'date': repo.last_commit_date,
                    'repo_name': repo.name,
                    'commits': repo.total_commits,
                    'message': repo.last_commit_message[:50] + '...' if len(repo.last_commit_message) > 50 else repo.last_commit_message
                })
        
        # Sort by date
        timeline_data.sort(key=lambda x: x['date'], reverse=True)

        return timeline_data[:10]  # return last 10 events
    
    @property
    def commit_summary(self):
        """Get a brief commit summary for display."""
        stats = self.get_commit_stats()
        if stats['total_commits'] == 0:
            return "No development activity tracked"
        
        return f"{stats['total_commits']} commits across {stats['repository_count']} repo(s)"

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

    # Testing additional methods for system list w GH data

    def _safe_days_since(self, date_or_datetime):
        """
        Safely calculate days since a date or datetime object.
        Handles both date and datetime objects correctly.
        """
        if not date_or_datetime:
            return None
        
        # Get today as a date
        today = timezone.now().date()
        
        # Convert input to date if it's a datetime
        if hasattr(date_or_datetime, 'date'):
            target_date = date_or_datetime.date()
        else:
            target_date = date_or_datetime
        
        return (today - target_date).days

    def get_enhanced_commit_stats(self):
        """
        Enhanced version of get_commit_stats that includes weekly data analysis
        """
        basic_stats = self.get_commit_stats()  # Use existing method

        # Add weekly analysis if available
        repos = self.github_repositories.all()

        if repos.exists():
            # Get recent weekly data (last 12 weeks)
            twelve_weeks_ago = timezone.now().date() - timedelta(weeks=12)

            recent_weeks = GitHubCommitWeek.objects.filter(
                repository__in=repos, week_start_date__gte=twelve_weeks_ago
            ).order_by("-year", "-week")

            if recent_weeks.exists():
                # Calculate weekly metrics
                total_weeks = recent_weeks.count()
                active_weeks = recent_weeks.filter(commit_count__gt=0).count()
                avg_commits_per_week = (
                    recent_weeks.aggregate(avg=models.Avg("commit_count"))["avg"] or 0
                )

                # Weekly consistency
                consistency_score = (
                    (active_weeks / total_weeks * 100) if total_weeks > 0 else 0
                )

                # Recent trend (compare last 4 weeks to previous 8 weeks)
                last_4_weeks = recent_weeks[:4]
                previous_8_weeks = recent_weeks[4:12]

                recent_avg = (
                    last_4_weeks.aggregate(avg=models.Avg("commit_count"))["avg"] or 0
                )

                previous_avg = (
                    previous_8_weeks.aggregate(avg=models.Avg("commit_count"))["avg"] or 0
                )

                if previous_avg > 0:
                    trend_percentage = ((recent_avg - previous_avg) / previous_avg) * 100
                else:
                    trend_percentage = 0 if recent_avg == 0 else 100

                # Add weekly analysis to basic stats
                basic_stats.update(
                    {
                        "weekly_analysis": {
                            "total_weeks_tracked": total_weeks,
                            "active_weeks": active_weeks,
                            "avg_commits_per_week": round(avg_commits_per_week, 1),
                            "consistency_score": round(consistency_score, 1),
                            "recent_trend": {
                                "percentage": round(trend_percentage, 1),
                                "direction": "up"
                                if trend_percentage > 5
                                else "down"
                                if trend_percentage < -5
                                else "stable",
                                "recent_avg": round(recent_avg, 1),
                                "previous_avg": round(previous_avg, 1),
                            },
                        }
                    }
                )

        return basic_stats

    def get_learning_velocity_with_github(self):
        """
        Enhanced learning velocity calculation that factors in GitHub activity
        """
        # Base learning velocity (skills per month)
        base_velocity = self.get_learning_velocity()

        # Get GitHub activity factor
        commit_stats = self.get_commit_stats()
        commits_per_month = commit_stats.get("avg_commits_per_month", 0)

        # GitHub activity multiplier (more commits = higher learning velocity indicator)
        if commits_per_month >= 20:
            github_factor = 1.3  # 30% boost for high activity
        elif commits_per_month >= 10:
            github_factor = 1.2  # 20% boost for good activity
        elif commits_per_month >= 5:
            github_factor = 1.1  # 10% boost for moderate activity
        else:
            github_factor = 1.0  # No change for low/no activity

        enhanced_velocity = base_velocity * github_factor

        return {
            "base_velocity": base_velocity,
            "github_factor": github_factor,
            "enhanced_velocity": round(enhanced_velocity, 2),
            "commits_per_month": commits_per_month,
        }

    def get_complexity_evolution_score_with_github(self):
        """
        UPDATED: Complexity evolution that uses real GitHub data instead of static
        """
        commit_stats = self.get_commit_stats()

        # Base factors
        base_complexity = self.complexity or 5
        skills_factor = min(self.skills_developed.count(), 5)  # Cap at 5

        # GitHub complexity factors (using real data)
        total_commits = commit_stats.get("total_commits", 0)
        repo_count = commit_stats.get("repository_count", 0)
        avg_commits_month = commit_stats.get("avg_commits_per_month", 0)

        # Commit volume factor
        if total_commits >= 150:
            commit_factor = 4
        elif total_commits >= 100:
            commit_factor = 3
        elif total_commits >= 50:
            commit_factor = 2
        elif total_commits >= 20:
            commit_factor = 1
        else:
            commit_factor = 0

        # Repository complexity (multiple repos indicate more complex project structure)
        repo_factor = min(repo_count, 3)  # Cap at 3

        # Development consistency factor (regular commits = higher complexity projects)
        if avg_commits_month >= 15:
            consistency_factor = 2
        elif avg_commits_month >= 8:
            consistency_factor = 1
        else:
            consistency_factor = 0

        # Learning stage progression factor
        stage_factors = {
            "tutorial": 0,
            "guided": 1,
            "independent": 2,
            "refactoring": 3,
            "contributing": 4,
            "teaching": 5,
        }
        stage_factor = stage_factors.get(self.learning_stage, 2)

        # Calculate final score
        total_score = (
            base_complexity
            + skills_factor
            + commit_factor
            + repo_factor
            + consistency_factor
            + stage_factor
        )

        return min(total_score, 20)  # Cap at 20 for ultra-complex projects

    def get_portfolio_readiness_score_with_github(self):
        """
        Enhanced portfolio readiness that factors in GitHub activity
        """
        # Base readiness score
        base_score = self.get_portfolio_readiness_score()

        commit_stats = self.get_commit_stats()

        # GitHub readiness factors
        github_bonus = 0

        # Recent activity bonus (shows project is actively maintained)
        commits_30_days = commit_stats.get("commits_last_30_days", 0)
        if commits_30_days >= 5:
            github_bonus += 10
        elif commits_30_days >= 1:
            github_bonus += 5

        # Total commits bonus (shows substantial work)
        total_commits = commit_stats.get("total_commits", 0)
        if total_commits >= 100:
            github_bonus += 15
        elif total_commits >= 50:
            github_bonus += 10
        elif total_commits >= 20:
            github_bonus += 5

        # Repository count bonus (multiple repos show broader skills)
        repo_count = commit_stats.get("repository_count", 0)
        if repo_count >= 3:
            github_bonus += 10
        elif repo_count >= 2:
            github_bonus += 5

        # Last commit recency (projects with recent commits are more portfolio-ready)
        last_commit_date = commit_stats.get('last_commit_date')
        days_since = self._safe_days_since(last_commit_date)
    
        if days_since is not None:
            if days_since <= 30:
                github_bonus += 10
            elif days_since <= 90:
                github_bonus += 5
        
        enhanced_score = min(base_score + github_bonus, 100)  # Cap at 100%

        return {
            "base_score": base_score,
            "github_bonus": github_bonus,
            "enhanced_score": enhanced_score,
            "factors": {
                "recent_activity": commits_30_days,
                "total_commits": total_commits,
                "repo_count": repo_count,
                "last_commit_days": days_since
            },
        }

    def get_development_timeline_with_commits(self):
        """
        Enhanced development timeline that includes real commit activity
        """
        timeline = []

        # Add learning milestones
        milestones = self.milestones.order_by("-date_achieved")[:5]
        for milestone in milestones:
            timeline.append(
                {
                    "type": "milestone",
                    "date": milestone.date_achieved.date(),
                    "title": milestone.title,
                    "description": milestone.description,
                    # "confidence": milestone.confidence_boost,
                }
            )

        # Add significant commit activity (using GitHubCommitWeek data)
        repos = self.github_repositories.all()
        if repos.exists():
            # Get weeks with significant activity (>= 10 commits)
            significant_weeks = GitHubCommitWeek.objects.filter(
                repository__in=repos, commit_count__gte=10
            ).order_by("-year", "-week")[:5]

            for week in significant_weeks:
                timeline.append(
                    {
                        "type": "development_sprint",
                        "date": week.week_start_date,
                        "title": f"Development Sprint - {week.commit_count} commits",
                        "description": f"High activity week in {week.repository.name}",
                        "repo": week.repository.name,
                        "commit_count": week.commit_count,
                    }
                )

        # Sort combined timeline by date
        timeline.sort(key=lambda x: x["date"], reverse=True)

        return timeline[:10]  # Return top 10 events

    def get_learning_stage_color_with_activity(self):
        """
        Enhanced learning stage color that considers GitHub activity
        """
        base_color = self.get_learning_stage_color()

        commit_stats = self.get_commit_stats()
        commits_30_days = commit_stats.get("commits_last_30_days", 0)

        # Modify color intensity based on recent activity
        if commits_30_days >= 10:
            # High activity - use brighter/more intense colors
            color_map = {
                "#FFB74D": "#FF9800",  # tutorial -> brighter orange
                "#81C784": "#4CAF50",  # guided -> brighter green
                "#64B5F6": "#2196F3",  # independent -> brighter blue
                "#BA68C8": "#9C27B0",  # refactoring -> brighter purple
                "#4FC3F7": "#00BCD4",  # contributing -> brighter cyan
                "#FFD54F": "#FFC107",  # teaching -> brighter yellow
            }
            return color_map.get(base_color, base_color)
        elif commits_30_days == 0:
            # No activity - use muted colors
            color_map = {
                "#FFB74D": "#FFCC80",  # tutorial -> muted orange
                "#81C784": "#A5D6A7",  # guided -> muted green
                "#64B5F6": "#90CAF9",  # independent -> muted blue
                "#BA68C8": "#CE93D8",  # refactoring -> muted purple
                "#4FC3F7": "#80DEEA",  # contributing -> muted cyan
                "#FFD54F": "#FFF176",  # teaching -> muted yellow
            }
            return color_map.get(base_color, base_color)

        return base_color  # Normal activity - keep original color

    # =========== Architecture Diagram Additions ==============
    def get_architecture_diagram(self):
        """
        Generate interactive 3D architecture diagram using Plotly.
        Returns HTML div ready for template embedding.
        """
        from .services.architecture_service import ArchitectureDiagramService

        service = ArchitectureDiagramService(self)
        return service.generate_plotly_diagram()
    
    def has_architecture_diagram(self):
        """Check if system has architecture components defined"""
        return self.architecture_components.exists()


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

    # Remove - use queries to determine #119
    # # Optional before/after tracking
    # skill_level_before = models.IntegerField(choices=[(i, i) for i in range(1, 6)], blank=True, null=True, help_text="Skill level before project (1-5, optional)")
    # skill_level_after = models.IntegerField(choices=[(i, i) for i in range(1, 6)], blank=True, null=True, help_text="Skill level after project (1-5, optional)")

    # === New for Skill-Tech Models Rework ===
    technologies_used = models.ManyToManyField(
        'Technology',
        blank=True,
        related_name='skill_applications',
        help_text='Which technologies were used to apply this skill in this project?'
    )

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
        return display_map.get(self.proficiency_gained, "Unknown")

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

    # Remove - use queries to determine #119
    # def get_skill_improvement(self):
    #     """Calculate improvement if before/after levels set"""
    #     if self.skill_level_before and self.skill_level_after:
    #         return self.skill_level_after - self.skill_level_before
    #     return None

    # Remove - use queries to determine #119
    # def has_improvement_data(self):
    #     """Check if before/after tracking is available"""
    #     return bool(self.skill_level_before and self.skill_level_after)

    def get_learning_context(self):
        """Get learning context for dashboard display"""
        return {
            'skill_name': self.skill.name,
            'system_title': self.system.title,
            'proficiency_gained': self.get_proficiency_display_short(),
            'color': self.get_proficiency_color(),
            'how_learned': self.how_learned,
            # 'improvement': self.get_skill_improvement(),
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

    # Removing - not useful - #120
    # # Learning impact (simple 1-5 scale)
    # difficulty_level = models.IntegerField(
    #     choices=[(i, f"Level {i}") for i in range(1, 6)],
    #     default=3,
    #     help_text="How challenging was this to achieve? (1=Easy, 5=Very Hard)"
    # )

    # confidence_boost = models.IntegerField(
    #     choices=[(i, f"{i} stars") for i in range(1, 6)],
    #     default=3,
    #     help_text="How much did this boost you confidence? (1-5 stars)"
    # )

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

    # Removing - #120
    # def get_difficulty_stars(self):
    #     """Visual difficulty representation"""
    #     return "★" * self.difficulty_level + "☆" * (5 - self.difficulty_level)

    # def get_confidence_stars(self):
    #     """Visual confidence boost representation"""
    #     return "★" * self.confidence_boost + "☆" * (5 - self.confidence_boost)

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
            # "difficulty": self.difficulty_level,
            # "confidence_boost": self.confidence_boost,
            "icon": self.get_milestone_icon(),
            "color": self.get_milestone_color(),
            "days_ago": self.days_since_achieved(),
            "has_post": bool(self.related_post),
            "shared": self.shared_publicly,
        }


class ArchitectureComponent(models.Model):
    """
    Defines individual components in a system's architecture diagram.
    Reusable across different projects with flexible configuration.
    """
    COMPONENT_TYPES = [
        ('frontend', 'Frontend Interface'),
        ('backend', 'Backend Service'),
        ('api', 'External API'),
        ('database', 'Data Storage'),
        ('processing', 'Data Processing'),
        ('file_io', 'File Input/Output'),
        ('authentication', 'Authentication'),
        ('deployment', 'Deployment/Hosting'),
        ('other', 'Other Component'),
    ]

    # Core identification
    system = models.ForeignKey(SystemModule, on_delete=models.CASCADE, related_name='architecture_components')
    name = models.CharField(max_length=100, help_text="Display name (e.g., 'Streamlit Frontend)")
    component_type = models.CharField(max_length=20, choices=COMPONENT_TYPES, default='other')

    # Visual Positioning
    position_x = models.FloatField(default=0.0, help_text="X coordinates in 3D space")
    position_y = models.FloatField(default=0.0, help_text="Y coordinates in 3D space")
    position_z = models.FloatField(default=0.0, help_text="Z coordinates in 3D space")

    # Visual Styling
    color = models.CharField(max_length=7, default='#00ffff', help_text="Hex color for component visualization")
    size = models.PositiveIntegerField(default=15, help_text="Visual size (10-30 recommended)")

    # Technical details
    technology = models.ForeignKey(Technology, on_delete=models.SET_NULL, null=True, blank=True, help_text="Primary technology used in this component")
    description = models.TextField(blank=True, help_text="Technical description for tooltips/hover info")

    # Relationships and flow
    display_order = models.PositiveIntegerField(default=0)
    is_core = models.BooleanField(default=False, help_text="Mark as core/central component")

    class Meta:
        ordering = ['display_order', 'name']
        unique_together = ('system', 'name')
    
    def __str__(self):
        return f"{self.system.title} - {self.name}"
    
    def get_hover_info(self):
        """Generate hover info for component."""
        info = [f"<b>{self.name}</b>"]
        if self.technology:
            info.append(f"Technology: {self.technology.name}")
        if self.description:
            info.append(f"Details: {self.description}")
        info.append(f"Type: {self.get_component_type_display()}")
        return "<br>".join(info)
    
    def get_component_type_icon(self):
        """Get font awesome icon based on component type"""
        icons = {
            "frontend": "desktop",
            "backend": "server",
            "api": "plug",
            "database": "database",
            "processing": "arrows-rotate",
            "file_io": "file-import",
            "authentication": "lock",
            "deployment": "rocket",
            "other": "cube"
        }
        return icons.get(self.component_type, "cube")


class ArchitectureConnection(models.Model):
    """
    Defines connections between architectture components.
    Represents data flow, dependencies, API calls, etc.
    """
    CONNECTION_TYPES = [
        ('data_flow', 'Data Flow'),
        ('api_call', 'API Request/Response'),
        ('dependency', 'Dependency'),
        ('file_transfer', 'File Transfer'),
        ('authentication', 'Authentication'),
        ('deployment', 'Deployment Pipeline'),
        ('user_interaction', 'User Interaction'),
    ]

    # Core relationship
    from_component = models.ForeignKey(ArchitectureComponent, on_delete=models.CASCADE, related_name='outgoing_connections')
    to_component = models.ForeignKey(ArchitectureComponent, on_delete=models.CASCADE, related_name='incoming_connections')

    # Connection details
    connection_type = models.CharField(max_length=20, choices=CONNECTION_TYPES, default='data_flow')
    label = models.CharField(max_length=50, blank=True, help_text="Label for connection line (e.g., 'Geocoding Request')")

    # Visual styling
    line_color = models.CharField(max_length=7, default='#00ffff', help_text="Color for connection line")
    line_width = models.PositiveIntegerField(default=2, help_text="Line thickness (1-5 recommended)")
    is_bidirectional = models.BooleanField(default=False, help_text="Two-way connection")

    class Meta:
        unique_together = ('from_component', 'to_component')
    
    def __str__(self):
        return f"{self.from_component.name} → {self.to_component.name}"
