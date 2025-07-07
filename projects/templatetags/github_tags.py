from django import template
from core.utils.github_helpers import GitHubDataProcessor

import re

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
