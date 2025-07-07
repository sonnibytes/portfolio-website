import requests
import logging
from typing import Dict, List, Optional, Union
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta
import time

import hashlib
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors."""
    pass


class GitHubAPIService:
    """
    GitHub API Integration service for Django.
    Handles authentication, rate limiting, caching, and error handling.
    """

    def __init__(self):
        self.config = settings.GITHUB_API_CONFIG
        self.base_url = self.config['BASE_URL']
        self.token = self.config['TOKEN']
        self.username = self.config['USERNAME']
        self.timeout = self.config['TIMEOUT']
        self.cache_timeout = self.config['CACHE_TIMEOUT']

        if not self.token:
            logger.warning("GitHub token not configured - API rate limits will apply")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers for GitHub API."""
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': f'AURA-Portfolio/{self.username}'
        }

        if self.token:
            headers['Authorization'] = f'token {self.token}'
        
        return headers
    
    def _create_cache_key(self, endpoint: str, params: Optional[Dict] = None) -> str:
        """
        Create a cache-safe key for memcached compatibility.
        Memcached keys must be under 250 chars and can only contain A-Z, a-z, 0-9, -, _
        """
        # Clean the endpoint - remove leading slashes and replace special chars
        clean_endpoint = endpoint.strip('/').replace('/', '_').replace('-', '_')

        # Create a hash of params if they exist
        if params:
            # Sort params for consistent hashing
            sorted_params = sorted(params.items())
            param_string = urlencode(sorted_params)
            param_hash = hashlib.md5(param_string.encode()).hexdigest()[:8]
            cache_key = f"github_api_{clean_endpoint}_{param_hash}"
        else:
            cache_key = f"github_api_{clean_endpoint}"
        
        # Ensure key is under 250 chars and contains only valid chars
        # Leave some margin
        if len(cache_key) > 240:
            # If too long, hash entire thing
            cache_key = f"github_api_{hashlib.md5(cache_key.encode()).hexdigest()}"
        
        return cache_key

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make authenticated request to GitHub API with error handling and rate limiting.

        NOTE TO SELF: Key diff from Flask: Django has built-in caching framework.
        """
        # Create cache-safe key
        cache_key = self._create_cache_key(endpoint, params)

        # Try to get from cache first
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Cache hit for {endpoint}")
            return cached_result
        
        # Make API request
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            logger.info(f"Making GitHub API request: {url}")
            response = requests.get(url, headers=self._get_headers(), params=params or {}, timeout=self.timeout)

            # Handle rate limiting
            if response.status_code == 403:
                rate_limit_remaining = response.headers.get('X-RateLimit-Remaining', '0')
                if rate_limit_remaining == 0:
                    reset_time = response.headers.get('X-RateLimit-Reset')
                    logger.error(f"GitHub API rate limit exceeded. Resets at {reset_time}")
                    raise GitHubAPIError("Rate limit exceeded")
            
            response.raise_for_status()
            data = response.json()

            # Cache successful results
            cache.set(cache_key, data, self.cache_timeout)
            logger.info(f"Cached GitHub API response for {endpoint}")

            return data
        
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API request failed: {e}")
            raise GitHubAPIError(f"API request failed: {e}")
    
    def get_user_info(self, username: Optional[str] = None) -> Dict:
        """Get GitHub user info"""
        username = username or self.username
        return self._make_request(f"users/{username}")
    
    def get_repositories(self, username: Optional[str] = None,
                         sort: str = 'updated', per_page: int = 30) -> List[Dict]:
        """Get repositories with sorting and pagination. Updated to get all for authenticated user, not just public"""
        username = username or self.username
        params = {
            'sort': sort,
            'per_page': per_page,
            'type': 'owner'  # Only repos owned by user
        }
        return self._make_request("user/repos", params)
    
    def get_repository_details(self, username: str, repo_name: str) -> Dict:
        """Get detailed info about specific repo"""
        return self._make_request(f"repos/{username}/{repo_name}")
    
    def get_repository_languages(self, username: str, repo_name: str) -> Dict:
        """Get programming languages used in repo"""
        return self._make_request(f"repos/{username}/{repo_name}/languages")
    
    def get_repository_commits(self, username: str, repo_name: str,
                               since: Optional[str] = None, per_page: int = 10) -> List[Dict]:
        """Get recent commits for a repo"""
        params = {'per_page': per_page}
        if since:
            params['since'] = since
        return self._make_request(f"repos/{username}/{repo_name}/commits", params)
    
    def get_user_stats(self, username: Optional[str] = None) -> Dict:
        """
        Get comprehensive GitHub stats for a user.
        This method aggregates data from multiple endpoints.
        """
        username = username or self.username

        # Get basic user info
        user_info = self.get_user_info(username)

        # Get repositories
        repos = self.get_repositories(username, per_page=100)

        # Calculate stats
        total_repos = len(repos)
        total_stars = sum(repo['stargazers_count'] for repo in repos)
        total_forks = sum(repo['forks_count'] for repo in repos)

        # Language analysis
        languages = {}
        for repo in repos[:20]:  # Analyze top 20 repos to avoid rate limits
            try:
                repo_languages = self.get_repository_languages(username, repo['name'])
                for lang, bytes_count in repo_languages.items():
                    languages[lang] = languages.get(lang, 0) + bytes_count
            except GitHubAPIError:
                continue  # Skip if language data unavailable
        
        # Sort languages by usage
        sorted_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)

        return {
            'user_info': user_info,
            'repositories': repos,
            'stats': {
                'total_repositories': total_repos,
                'total_stars': total_stars,
                'total_forks': total_forks,
                'top_languages': sorted_languages[:10],
                'recent_repos': sorted(repos, key=lambda x: x['updated_at'], reverse=True)[:5]
            }
        }
