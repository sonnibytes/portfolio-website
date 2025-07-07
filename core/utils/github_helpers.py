from datetime import datetime, timedelta
from django.utils import timezone
from typing import Dict, List, Optional
import re


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
    def is_active_repository(updated_at: str, threshold_days: int = 90) -> bool:
        """Check if repository is considered active."""
        try:
            update_date = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
            threshold = timezone.now() - timedelta(days=threshold_days)
            return update_date >= threshold
        except (ValueError, AttributeError):
            return False

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