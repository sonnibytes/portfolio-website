from django import template
from django.utils import timezone
from django.utils.safestring import mark_safe
from core.utils.github_helpers import GitHubDataProcessor

import re
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Avg
from projects.models import GitHubCommitWeek

register = template.Library()

@register.filter
def language_color(language):
    """Get color for programming language."""
    return GitHubDataProcessor.get_language_color(language)


@register.filter
def format_repo_size(size_kb):
    """Format repo size."""
    return GitHubDataProcessor.format_repo_size(size_kb)


@register.filter
def is_active_repo(updated_at):
    """Check if repo is active."""
    return GitHubDataProcessor.is_active_repository(updated_at)


@register.filter
def github_username_from_url(url):
    """Extract username from GitHub URL."""
    match = re.search(r'github\.com/([^/]+)', url)
    return match.group(1) if match else ''


@register.inclusion_tag('projects/components/repo_language_bar.html')
def repo_language_bar(repository):
    """Render language breakdown bar for repository."""
    languages = repository.languages.all()
    return {'languages': languages}


@register.filter
def commit_frequency_badge(rating):
    """Generate badge for commit frequency rating."""
    badges = {
        5: '<span class="badge badge-success">Very Active</span>',
        4: '<span class="badge badge-primary">Active</span>',
        3: '<span class="badge badge-warning">Moderate</span>',
        2: '<span class="badge badge-secondary">Low Activity</span>',
        1: '<span class="badge badge-light">Inactive</span>',
    }
    return mark_safe(badges.get(rating, badges[1]))


@register.filter
def format_commit_count(count):
    """Format commit count for display."""
    if count >= 1000:
        return f"{count / 1000:.1f}k"
    return str(count)


@register.filter
def days_since_commit(commit_date):
    """Calculate days since commit."""
    if not commit_date:
        return "Never"
    
    if isinstance(commit_date, str):
        commit_date = datetime.fromisoformat(commit_date.replace('Z', '+00:00'))
    
    days = (timezone.now() - commit_date).days

    if days == 0:
        return "Today"
    elif days == 1:
        return "Yesterday"
    elif days < 7:
        return f"{days} days ago"
    elif days < 30:
        weeks = days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    else:
        months = days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"


@register.inclusion_tag('projects/components/commit_summary.html')
def commit_summary_card(system_module):
    """Render commit summary card for a system module."""
    commit_stats = system_module.get_commit_stats()
    return {'stats': commit_stats, 'system': system_module}

@register.inclusion_tag("projects/components/github_weekly_panel.html")
def github_weekly_panel(repo=None, weeks_back=12, panel_style="dashboard"):
    """
    Display weekly commit activity panel.
    Can show data for specific repo or all system-linked repos.
    """
    from projects.models import (
        GitHubRepository,
    )  # Import here to avoid circular imports

    if repo:
        # Single repository data
        weekly_data = repo.get_weekly_commit_data(weeks_back=weeks_back)
        monthly_data = repo.get_monthly_commit_data(months_back=6)
        repo_name = repo.name
        context_title = f"Weekly Activity - {repo.name}"
    else:
        # All system-linked repositories
        repos = GitHubRepository.objects.with_detailed_tracking()
        weekly_data = GitHubCommitWeek.objects.filter(repository__in=repos).order_by(
            "-year", "-week"
        )[:weeks_back]

        # Aggregate monthly data
        monthly_data = []
        monthly_totals = (
            GitHubCommitWeek.objects.filter(repository__in=repos)
            .values("year", "month", "month_name")
            .annotate(
                total_commits=Sum("commit_count"),
                avg_weekly=Avg("commit_count"),
                weeks_count=Count("id"),
            )
            .order_by("-year", "-month")[:6]
        )

        for month in monthly_totals:
            monthly_data.append(
                {
                    "year": month["year"],
                    "month": month["month"],
                    "month_name": month["month_name"],
                    "total_commits": month["total_commits"],
                    "avg_commits_per_week": round(month["avg_weekly"], 1),
                    "weeks_count": month["weeks_count"],
                }
            )

        repo_name = "All Projects"
        context_title = "Development Activity Overview"

    # Calculate trends and metrics using GitHubDataProcessor
    metrics = GitHubDataProcessor.format_weekly_metrics(weekly_data)
    trend = GitHubDataProcessor.calculate_commit_trend(weekly_data)
    trend_info = GitHubDataProcessor.get_trend_icon_and_color(trend)

    # Add trend info to metrics
    metrics.update(
        {
            "trend": trend,
            "trend_icon": trend_info["icon"],
            "trend_color": trend_info["color"],
        }
    )

    return {
        "weekly_data": weekly_data,
        "monthly_data": monthly_data,
        "repo_name": repo_name,
        "title": context_title,
        "panel_style": panel_style,
        "metrics": metrics,
        "chart_data": GitHubDataProcessor.prepare_weekly_chart_data(
            weekly_data, monthly_data
        ),
    }


@register.inclusion_tag("projects/components/github_repo_card.html")
def github_repo_card(repo, show_weekly_summary=True):
    """Enhanced repository card with weekly data."""
    weekly_summary = None
    monthly_summary = None

    if show_weekly_summary and repo.enable_detailed_tracking:
        weekly_summary = repo.get_weekly_commit_summary()
        monthly_summary = repo.get_monthly_commit_summary()

    return {
        "repo": repo,
        "weekly_summary": weekly_summary,
        "monthly_summary": monthly_summary,
        "show_weekly": show_weekly_summary,
    }


@register.filter
def weekly_commit_chart_color(trend):
    """Get chart color based on trend."""
    return GitHubDataProcessor.get_chart_color_for_trend(trend)


@register.filter
def format_commit_count_enhanced(count):
    """Enhanced commit count formatting."""
    if count == 0:
        return "No commits"
    elif count == 1:
        return "1 commit"
    else:
        return f"{count} commits"


@register.filter
def trend_badge_class(trend):
    """Get CSS class for trend badge."""
    classes = {
        "increasing": "trend-badge success",
        "decreasing": "trend-badge warning",
        "stable": "trend-badge info",
        "insufficient-data": "trend-badge secondary",
        "no-data": "trend-badge secondary",
    }
    return classes.get(trend, classes["no-data"])


@register.simple_tag
def weekly_activity_summary(repos_with_tracking):
    """Get weekly activity summary for all tracked repos."""
    if not repos_with_tracking.exists():
        return None

    # Get recent weekly data (last 4 weeks)
    recent_weeks = GitHubCommitWeek.objects.filter(
        repository__in=repos_with_tracking
    ).order_by("-year", "-week")[:4]

    if not recent_weeks:
        return None

    # Calculate stats
    total_recent_commits = sum(week.commit_count for week in recent_weeks)
    avg_commits_per_week = total_recent_commits / 4 if recent_weeks else 0

    # Most active repo this month
    current_month = timezone.now().month
    current_year = timezone.now().year

    most_active_repo = (
        GitHubCommitWeek.objects.filter(
            repository__in=repos_with_tracking, year=current_year, month=current_month
        )
        .values("repository__name")
        .annotate(total_commits=Sum("commit_count"))
        .order_by("-total_commits")
        .first()
    )

    return {
        "total_tracked_repos": repos_with_tracking.count(),
        "total_recent_commits": total_recent_commits,
        "avg_commits_per_week": round(avg_commits_per_week, 1),
        "most_active_repo": most_active_repo,
        "tracking_active": True,
    }


@register.filter
def get_week_label(week):
    """Get human readable week label."""
    if hasattr(week, "get_week_label"):
        return week.get_week_label()
    elif hasattr(week, "is_current_week") and week.is_current_week:
        return "This week"
    else:
        return f"Week {week.week}"


@register.filter
def commits_activity_class(commit_count):
    """Get CSS class for commit activity level."""
    if commit_count == 0:
        return "inactive"
    elif commit_count >= 10:
        return "very-active"
    elif commit_count >= 5:
        return "active"
    else:
        return "moderate"