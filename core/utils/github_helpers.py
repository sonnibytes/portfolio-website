from datetime import datetime, timedelta
from django.utils import timezone
from typing import Dict, List, Optional
import re
import json

class GitHubDataProcessor:
    """Utility class for processing GitHub data."""

    @staticmethod
    def calculate_language_percentages(languages_data: Dict[str, int]) -> List[Dict]:
        """Calculate percentage breakdown of languages."""
        total_bytes = sum(languages_data.values())

        if total_bytes == 0:
            return []
        
        percentages = []
        for language, bytes_count in languages_data.items():
            percentage = (bytes_count / total_bytes) * 100
            percentages.append({
                'language': language,
                'bytes': bytes_count,
                'percentage': round(percentage, 2)
            })
        
        return sorted(percentages, key=lambda x: x['percentage'], reverse=True)
    
    @staticmethod
    def get_language_color(language: str) -> str:
        """Get color code for programming language."""
        language_colors = {
            "Python": "#3776ab",
            "JavaScript": "#f7df1e",
            "TypeScript": "#3178c6",
            "HTML": "#e34f26",
            "CSS": "#1572b6",
            "Java": "#ed8b00",
            "C++": "#00599c",
            "C": "#a8b9cc",
            "Go": "#00add8",
            "Rust": "#000000",
            "PHP": "#777bb4",
            "Ruby": "#cc342d",
            "Swift": "#fa7343",
            "Kotlin": "#7f52ff",
            "Dart": "#0175c2",
            "Shell": "#89e051",
            "PowerShell": "#012456",
            "Dockerfile": "#384d54",
            "Jupyter Notebook": "#da5b0b",
        }

        return language_colors.get(language, "#6c757d")  # Default gray
    
    @staticmethod
    def format_repo_size(size_kb: int) -> str:
        """Format repository size in human-readable format."""
        if size_kb < 1024:
            return f"{size_kb} KB"
        elif size_kb < 1024 * 1024:
            return f"{size_kb / 1024:.1f} MB"
        else:
            return f"{size_kb / (1024 * 1024):.1f} GB"

    @staticmethod
    def extract_repo_topics(repo_data: Dict) -> List[str]:
        """Extract and clean repository topics."""
        topics = repo_data.get("topics", [])

        # Filter out common noise topics
        filtered_topics = [
            topic
            for topic in topics
            if not topic.lower() in ["hacktoberfest", "good-first-issue"]
        ]

        return filtered_topics[:5]  # Limit to 5 most relevant topics

    @staticmethod
    def is_active_repository(updated_at, threshold_days: int = 90) -> bool:
        """Check if repository is considered active."""
        if not updated_at:
            return False
        
        # Handle different input types
        if isinstance(updated_at, str):
            # Parse string datetime
            try:
                if updated_at.endswith('Z'):
                    # GitHub API format
                    updated_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                else:
                    # Try parsing as ISO format
                    updated_date = datetime.fromisoformat(updated_at)
            except ValueError:
                # If parsing fails, assume it's not active
                return False
        else:
            # Assume it's already a datetime object (from Django)
            updated_date = updated_at
        
        # Make sure we're comparing timezone-aware datetimes
        if updated_date.tzinfo is None:
            # If naive datetime, assume UTC
            updated_date = updated_date.replace(tzinfo=timezone.utc)
        
        # Calculate days since update
        now = timezone.now()
        days_since_update = (now - updated_date).days
        
        return days_since_update <= threshold_days

    @staticmethod
    def generate_repo_summary(repo_data: Dict) -> str:
        """Generate AI-like summary for repository."""
        name = repo_data.get("name", "Unknown")
        language = repo_data.get("language", "Mixed")
        stars = repo_data.get("stargazers_count", 0)
        forks = repo_data.get("forks_count", 0)

        # Simple template-based summary
        if stars > 100:
            popularity = "highly popular"
        elif stars > 10:
            popularity = "well-received"
        else:
            popularity = "emerging"

        return f"{name} is a {popularity} {language} project with {stars} stars and {forks} forks."
    
    @staticmethod
    def prepare_weekly_chart_data(weekly_data, monthly_data=None):
        """Prepare data for Chart.js weekly/monthly visualization with proper JSON serialization."""
        if not weekly_data:
            return {
                'labels': json.dumps([]),
                'weekly': json.dumps([]),
                'monthly_labels': json.dumps([]),
                'monthly': json.dumps([])
            }
        
        # Weekly chart data (last 12 weeks)
        weekly_labels = []
        weekly_commits = []
        
        for week in weekly_data:
            week_label = f"W{week.week}"
            if hasattr(week, 'is_current_week') and week.is_current_week:
                week_label += " (Current)"
            elif hasattr(week, 'get_week_label'):
                week_label_text = week.get_week_label()
                if week_label_text == "Last week":
                    week_label += " (Last)"
            
            weekly_labels.append(week_label)
            weekly_commits.append(week.commit_count)
        
        # Monthly chart data
        monthly_labels = []
        monthly_commits = []
        
        if monthly_data:
            for month in monthly_data:
                if isinstance(month, dict):
                    monthly_labels.append(f"{month['month_name'][:3]} {month['year']}")
                    monthly_commits.append(month['total_commits'])
                else:
                    # Handle model instances
                    monthly_labels.append(f"{month.month_name[:3]} {month.year}")
                    monthly_commits.append(getattr(month, 'total_commits', 0))
        
        # Return JSON-serialized data ready for template use
        return {
            'labels': json.dumps(list(reversed(weekly_labels))),  # Oldest to newest for chart
            'weekly': json.dumps(list(reversed(weekly_commits))),
            'monthly_labels': json.dumps(list(reversed(monthly_labels))),
            'monthly': json.dumps(list(reversed(monthly_commits)))
        }

    @staticmethod
    def calculate_commit_trend(weekly_data, weeks=4):
        """Calculate commit trend from weekly data."""
        if not weekly_data or len(weekly_data) < 2:
            return "insufficient-data"
        
        recent_weeks = list(weekly_data)[:weeks]
        commits = [week.commit_count for week in recent_weeks]
        
        if len(commits) < 2:
            return "insufficient-data"
        
        # Simple trend calculation
        first_half = sum(commits[:len(commits)//2])
        second_half = sum(commits[len(commits)//2:])
        
        if second_half > first_half * 1.2:
            return "increasing"
        elif second_half < first_half * 0.8:
            return "decreasing"
        else:
            return "stable"

    @staticmethod
    def get_trend_icon_and_color(trend):
        """Get icon and color for commit trend."""
        trend_mapping = {
            'increasing': {'icon': 'fas fa-trending-up', 'color': 'success'},
            'decreasing': {'icon': 'fas fa-trending-down', 'color': 'warning'},
            'stable': {'icon': 'fas fa-minus', 'color': 'info'},
            'insufficient-data': {'icon': 'fas fa-question', 'color': 'secondary'},
            'no-data': {'icon': 'fas fa-question', 'color': 'secondary'}
        }
        return trend_mapping.get(trend, trend_mapping['no-data'])

    @staticmethod
    def format_weekly_metrics(weekly_data):
        """Format weekly data for display metrics."""
        if not weekly_data:
            return {
                'recent_commits': 0,
                'total_weeks_tracked': 0,
                'avg_commits_per_week': 0,
                'most_active_week': None
            }
        
        # Recent commits (last 4 weeks)
        recent_4_weeks = list(weekly_data)[:4]
        recent_commits = sum(week.commit_count for week in recent_4_weeks)
        
        # Total tracked weeks
        total_weeks = len(weekly_data)
        
        # Average commits per week
        total_commits = sum(week.commit_count for week in weekly_data)
        avg_commits_per_week = round(total_commits / total_weeks, 1) if total_weeks > 0 else 0
        
        # Most active week
        most_active_week = max(weekly_data, key=lambda w: w.commit_count) if weekly_data else None
        
        return {
            'recent_commits': recent_commits,
            'total_weeks_tracked': total_weeks,
            'avg_commits_per_week': avg_commits_per_week,
            'most_active_week': most_active_week
        }

    @staticmethod
    def get_chart_color_for_trend(trend):
        """Get chart color based on trend."""
        colors = {
            'increasing': '#10b981',  # Green
            'stable': '#3b82f6',      # Blue  
            'decreasing': '#f59e0b',  # Orange
            'no-data': '#6b7280'      # Gray
        }
        return colors.get(trend, '#6b7280')