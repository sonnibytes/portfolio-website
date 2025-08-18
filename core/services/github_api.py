import requests
import logging
from typing import Dict, List, Optional, Union
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta
import time
import json

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
    
    def get_repository_commit_stats(self, username: str, repo_name: str,
                                    since_date: Optional[str] = None) -> Dict:
        """
        Get commit stats for a repository efficiently.
        Uses commit API with pagination to get accurate counts.
        """
        # Get total commit count using more efficient approach
        # First, try to get recent commits to check activity
        recent_commits = self.get_repository_commits(username, repo_name, per_page=100)

        if not recent_commits:
            return {
                'total_commits': 0,
                'last_commit_date': None,
                'last_commit_sha': '',
                'last_commit_message': '',
                'commits_last_30_days': 0,
                'commits_last_year': 0
            }
        
        # Get the most recent commit info
        latest_commit = recent_commits[0]
        last_commit_date = latest_commit['commit']['author']['date']
        last_commit_sha = latest_commit['sha']
        last_commit_message = latest_commit['commit']['message']

        # Calculate time-based commit counts
        now = datetime.now()
        thirty_days_ago = (now - timedelta(days=30)).isoformat() + 'Z'
        one_year_ago = (now - timedelta(days=365)).isoformat() + 'Z'

        # Count commits in last 30 days
        commits_30_days = self._count_commits_since(username, repo_name, thirty_days_ago)

        # Count commits in last year
        commits_year = self._count_commits_since(username, repo_name, one_year_ago)

        # For total commits, use reasonable approximation
        # Getting exact amount would require paginating through all commits (expensive)
        total_commits = self._estimate_total_commits(username, repo_name, recent_commits)

        return {
            'total_commits': total_commits,
            'last_commit_date': last_commit_date,
            'last_commit_sha': last_commit_sha,
            'last_commit_message': last_commit_message,
            'commits_last_30_days': commits_30_days,
            'commits_last_year': commits_year
        }
    
    def _count_commits_since(self, username: str, repo_name: str, since_date: str) -> int:
        """Count commits since a specific date."""
        try:
            commits = self.get_repository_commits(username, repo_name, since=since_date, per_page=100)
            return len(commits)
        except GitHubAPIError:
            return 0
        
    def _estimate_total_commits(self, username: str, repo_name: str, recent_commits: List[Dict]) -> int:
        """
        Estimate total commits using repo creation date and recent activity.
        This is more efficient than paging through all commits.
        """
        if not recent_commits:
            return 0
        
        try:
            # Get repo creation date
            repo_info = self.get_repository_details(username, repo_name)
            created_date = datetime.fromisoformat(repo_info['created_at'].replace('Z', '+00:00'))

            # If we have 100 recent commits, est based on repo age and activity
            if len(recent_commits) >= 100:
                # Active repo - estimate higher
                repo_age_months = (datetime.now() - created_date.replace(tzinfo=None)).days / 30
                estimated_monthly_commits = max(10, len(recent_commits) / 3)  # Conservative estimate
                return int(repo_age_months * estimated_monthly_commits)
            else:
                # Less active - use actual count as reasonable estimate
                return len(recent_commits)
        except Exception:
            # Fallback to just the commits we found
            return len(recent_commits)
    
    def sync_repository_commits(self, username: str, repo_name: str) -> Dict:
        """
        Sync commit data for a specific repo.
        Returns commit stats and metadata.
        """
        try:
            logger.info(f"Syncing commits for {username}/{repo_name}")

            # Get commit stats
            commit_stats = self.get_repository_commit_stats(username, repo_name)

            # Calculate avg commits per month
            repo_info = self.get_repository_details(username, repo_name)
            created_date = datetime.fromisoformat(repo_info['created_at'].replace('Z', '+00:00'))
            repo_age_months = max(1, (datetime.now() - created_date.replace(tzinfo=None)).days / 30)

            avg_commits_per_month = commit_stats['total_commits'] / repo_age_months

            # Add calculated fields
            commit_stats.update(
                {
                    "avg_commits_per_month": round(avg_commits_per_month, 2),
                    "commits_last_synced": timezone.now().isoformat(),
                    "repo_age_months": round(repo_age_months, 1),
                }
            )

            logger.info(
                f"Synced {commit_stats['total_commits']} commits for {repo_name}"
            )
            return commit_stats

        except GitHubAPIError as e:
            logger.error(f"Failed to sync commits for {repo_name}: {e}")
            return {}
        
    # ======== DETAILED COMMIT ACTIVITY ===========
    def get_repository_commit_activity(self, username: str, repo_name: str,
                                       etag: Optional[str] = None) -> Dict:
        """
        Get weekly commit activity using GitHub's commit activity endpoint.
        This endpoint provides commit counts for each week of the last year.
        
        Returns data in format:
        [
            {
                "week": 1302998400,  # Unix timestamp of week start
                "total": 11,         # Total commits
                "days": [0,3,2,2,1,0,3]  # Commits per day (Sun-Sat)
            }
        ]
        """
        # Use conditional request with ETag if provided
        headers = self._get_headers()
        if etag:
            headers['If-None-Match'] = etag
        
        endpoint = f"repos/{username}/{repo_name}/stats/commit_activity"
        
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = requests.get(url, headers=headers, timeout=self.timeout)
            
            # Handle 304 Not Modified - no changes since last request
            if response.status_code == 304:
                logger.info(f"No changes in commit activity for {repo_name} (304)")
                return {
                    'status': 'not_modified',
                    'etag': etag,
                    'data': []
                }
            
            # Handle 202 Accepted - GitHub is computing stats
            if response.status_code == 202:
                logger.info(f"GitHub computing stats for {repo_name} (202)")
                return {
                    'status': 'computing',
                    'retry_after': 5,  # Seconds to wait before retry
                    'data': []
                }
            
            response.raise_for_status()
            data = response.json()
            
            # Get ETag for future conditional requests
            new_etag = response.headers.get('ETag', '')
            
            return {
                'status': 'success',
                'etag': new_etag,
                'data': data
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub commit activity request failed: {e}")
            raise GitHubAPIError(f"Commit activity request failed: {e}")

    def get_repository_weekly_commits(self, username: str, repo_name: str,
                                      weeks_back: int = 52) -> List[Dict]:
        """
        Get weekly commit data in a more digestible format.
        Converts GitHub's commit activity data to weekly summaries.
        """
        activity_data = self.get_repository_commit_activity(username, repo_name)
        
        if activity_data['status'] != 'success':
            return []
        
        weekly_commits = []
        for week_data in activity_data['data']:
            # Convert Unix timestamp to datetime
            week_start = datetime.fromtimestamp(week_data['week'])
            year, week_num, _ = week_start.isocalendar()
            
            weekly_commits.append({
                'year': year,
                'week': week_num,
                'week_start': week_start.date(),
                'week_end': (week_start + timedelta(days=6)).date(),
                'commit_count': week_data['total'],
                'daily_commits': week_data['days'],  # [Sun, Mon, Tue, Wed, Thu, Fri, Sat]
            })
        
        # Sort by most recent first and limit to requested weeks
        weekly_commits.sort(key=lambda x: (x['year'], x['week']), reverse=True)
        return weekly_commits[:weeks_back]

    def sync_repository_weekly_commits(self, username: str, repo_name: str,
                                       etag: Optional[str] = None) -> Dict:
        """
        Sync weekly commit data for a specific repository.
        Returns weekly data along with metadata for database storage.
        """
        try:
            logger.info(f"Syncing weekly commits for {username}/{repo_name}")
            
            # Get commit activity data
            activity_response = self.get_repository_commit_activity(username, repo_name, etag)
            
            # Handle different response statuses
            if activity_response['status'] == 'not_modified':
                return {
                    'status': 'not_modified',
                    'etag': activity_response['etag'],
                    'weeks_updated': 0
                }
            
            if activity_response['status'] == 'computing':
                return {
                    'status': 'computing',
                    'retry_after': activity_response['retry_after']
                }
            
            # Process successful response
            weekly_data = []
            for week_data in activity_response['data']:
                week_start = datetime.fromtimestamp(week_data['week'])
                year, week_num, _ = week_start.isocalendar()
                
                weekly_data.append({
                    'year': year,
                    'week': week_num,
                    'week_start_date': week_start.date(),
                    'week_end_date': (week_start + timedelta(days=6)).date(),
                    'commit_count': week_data['total'],
                    'daily_breakdown': week_data['days'],
                    # Calculate additional metrics
                    'lines_added': 0,     # Would need separate API calls for this
                    'lines_deleted': 0,
                    'files_changed': 0,
                })
            
            return {
                'status': 'success',
                'etag': activity_response['etag'],
                'weekly_data': weekly_data,
                'weeks_updated': len(weekly_data),
                'last_sync': timezone.now().isoformat()
            }
            
        except GitHubAPIError as e:
            logger.error(f"Failed to sync weekly commits for {repo_name}: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

    def get_enhanced_repository_stats(self, username: str, repo_name: str) -> Dict:
        """
        Get comprehensive repository statistics including weekly data.
        Combines multiple GitHub API endpoints efficiently.
        """
        try:
            stats = {}
            
            # Basic repository info
            repo_info = self.get_repository_details(username, repo_name)
            stats['repository'] = repo_info
            
            # Commit activity (weekly)
            weekly_commits = self.get_repository_weekly_commits(username, repo_name)
            stats['weekly_commits'] = weekly_commits
            
            # Calculate derived metrics
            if weekly_commits:
                total_commits_year = sum(week['commit_count'] for week in weekly_commits)
                active_weeks = len([w for w in weekly_commits if w['commit_count'] > 0])
                avg_commits_per_week = total_commits_year / len(weekly_commits) if weekly_commits else 0
                
                # Recent activity (last 4 weeks)
                recent_commits = sum(week['commit_count'] for week in weekly_commits[:4])
                
                stats['derived_metrics'] = {
                    'total_commits_last_year': total_commits_year,
                    'active_weeks_last_year': active_weeks,
                    'avg_commits_per_week': round(avg_commits_per_week, 2),
                    'commits_last_4_weeks': recent_commits,
                    'activity_consistency': round(active_weeks / len(weekly_commits) * 100, 1) if weekly_commits else 0
                }
            
            return stats
            
        except GitHubAPIError as e:
            logger.error(f"Failed to get enhanced stats for {repo_name}: {e}")
            return {}

    def bulk_sync_weekly_commits(self, username: str, repo_names: List[str],
                                 delay_between_requests: float = 0.5) -> Dict:
        """
        Efficiently sync weekly commit data for multiple repositories.
        Includes delays to respect rate limits and handles GitHub's async stats computation.
        """
        results = {
            'successful': [],
            'failed': [],
            'computing': [],
            'not_modified': []
        }
        
        for i, repo_name in enumerate(repo_names):
            try:
                logger.info(f"Syncing weekly commits {i + 1}/{len(repo_names)}: {repo_name}")
                
                # Get any existing ETag from database
                # This would be passed in from the calling code
                etag = None  # Would come from GitHubRepository.stats_etag
                
                result = self.sync_repository_weekly_commits(username, repo_name, etag)
                
                if result['status'] == 'success':
                    results['successful'].append({
                        'repo': repo_name,
                        'weeks_updated': result['weeks_updated'],
                        'etag': result['etag']
                    })
                elif result['status'] == 'computing':
                    results['computing'].append(repo_name)
                elif result['status'] == 'not_modified':
                    results['not_modified'].append(repo_name)
                else:
                    results['failed'].append({
                        'repo': repo_name,
                        'error': result.get('error', 'Unknown error')
                    })
                
                # Delay between requests to be nice to GitHub's API
                if i < len(repo_names) - 1:  # Don't delay after the last request
                    time.sleep(delay_between_requests)
                    
            except Exception as e:
                logger.error(f"Unexpected error syncing {repo_name}: {e}")
                results['failed'].append({
                    'repo': repo_name,
                    'error': str(e)
                })
        
        logger.info(f"Bulk sync completed: {len(results['successful'])} successful, "
                    f"{len(results['failed'])} failed, {len(results['computing'])} computing")
        
        return results
