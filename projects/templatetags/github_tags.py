from django import template
from django.utils import timezone
from django.utils.safestring import mark_safe
from core.utils.github_helpers import GitHubDataProcessor

import re
from datetime import datetime, timedelta

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
