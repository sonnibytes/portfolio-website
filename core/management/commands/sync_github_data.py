from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from django.db import transaction
from core.services.github_api import GitHubAPIService, GitHubAPIError
from projects.models import GitHubRepository, GitHubLanguage, GitHubCommitWeek
import logging
from datetime import timedelta
import time

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Enhanced GitHub repository sync with weekly commit tracking"

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='GitHub username to sync (defaults to configured username)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if recently synced',
        )
        parser.add_argument(
            '--commits-only',
            action='store_true',
            help='Only sync commit data for existing repos',
        )
        parser.add_argument(
            '--weekly-only',
            action='store_true',
            help='Only sync weekly commit data for system-linked repos',
        )
        parser.add_argument(
            '--limit-repos',
            type=int,
            default=20,
            help='Limit number of repos to sync commits for (to avoid rate limits)',
        )
        parser.add_argument(
            '--system-repos-only',
            action='store_true',
            help='Only sync repositories linked to systems',
        )
    
    def handle(self, *args, **options):
        github_service = GitHubAPIService()
        username = options.get('username') or github_service.username
        force_update = options.get('force', False)
        commits_only = options.get('commits_only', False)
        weekly_only = options.get('weekly_only', False)
        system_repos_only = options.get('system_repos_only', False)
        repo_limit = options.get('limit_repos', 20)

        if not username:
            self.stdout.write(
                self.style.ERROR('No GitHub username configured or provided')
            )
            return
        
        try:
            if weekly_only:
                self.sync_weekly_commits_only(github_service, username, force_update)
            elif commits_only:
                self.sync_commits_only(github_service, username, force_update, repo_limit)
            else:
                self.sync_full_data(github_service, username, force_update, repo_limit, system_repos_only)

        except GitHubAPIError as e:
            self.stdout.write(
                self.style.ERROR(f'GitHub API error: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error: {e}')
            )
    
    def sync_weekly_commits_only(self, github_service, username, force_update):
        """Sync only weekly commit data for system-linked repositories."""
        self.stdout.write(self.style.SUCCESS('=== WEEKLY COMMIT SYNC ==='))
        
        # Get repositories that need weekly commit sync
        if force_update:
            repos_to_sync = GitHubRepository.objects.with_detailed_tracking()
        else:
            repos_to_sync = GitHubRepository.objects.needs_weekly_sync(hours_threshold=24)
        
        if not repos_to_sync:
            self.stdout.write('No repositories need weekly commit sync.')
            return
        
        self.stdout.write(f'Found {repos_to_sync.count()} repositories needing weekly sync...')
        
        # Bulk sync for efficiency
        repo_names = [repo.name for repo in repos_to_sync]
        
        # Get ETags for conditional requests
        etag_map = {
            repo.name: repo.stats_etag
            for repo in repos_to_sync
            if repo.stats_etag
        }
        
        success_count = 0
        computing_count = 0
        not_modified_count = 0
        error_count = 0
        
        for repo in repos_to_sync:
            try:
                self.stdout.write(f'  → Syncing weekly data for {repo.name}...')
                
                # Get existing ETag for conditional request
                etag = repo.stats_etag if repo.stats_etag else None
                
                # Sync weekly commit data
                result = github_service.sync_repository_weekly_commits(
                    username, repo.name, etag
                )
                
                if result['status'] == 'success':
                    # Update repository with new ETag and sync time
                    repo.stats_etag = result['etag']
                    repo.commit_weeks_last_synced = timezone.now()
                    repo.save()
                    
                    # Store weekly data
                    weeks_created = self.store_weekly_commit_data(repo, result['weekly_data'])
                    
                    success_count += 1
                    self.stdout.write(
                        f'    ✓ {weeks_created} weeks of data updated'
                    )
                    
                elif result['status'] == 'not_modified':
                    # Update sync time even if data unchanged
                    repo.commit_weeks_last_synced = timezone.now()
                    repo.save()
                    
                    not_modified_count += 1
                    self.stdout.write(
                        '    ≈ No changes since last sync'
                    )
                    
                elif result['status'] == 'computing':
                    computing_count += 1
                    self.stdout.write(
                        '    ⏳ GitHub computing stats (will retry later)'
                    )
                    
                else:
                    error_count += 1
                    error_msg = result.get('error', 'Unknown error')
                    self.stdout.write(
                        self.style.WARNING(f'    ✗ Failed: {error_msg}')
                    )
                
                # Small delay between requests
                time.sleep(0.2)
                
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.WARNING(f'    ✗ Exception: {str(e)}')
                )
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\nWeekly sync completed:\n'
                f'  ✓ {success_count} successful\n'
                f'  ≈ {not_modified_count} unchanged\n'
                f'  ⏳ {computing_count} computing\n'
                f'  ✗ {error_count} errors'
            )
        )
    
    def store_weekly_commit_data(self, repository, weekly_data):
        """Store weekly commit data in database efficiently with month metadata."""
        weeks_created = 0
        
        with transaction.atomic():
            for week_data in weekly_data:
                # Calculate month metadata
                start_date = week_data['week_start_date']
                month = start_date.month
                month_name = start_date.strftime('%B')
                quarter = (month - 1) // 3 + 1
                
                # Use get_or_create to handle duplicates
                commit_week, created = GitHubCommitWeek.objects.get_or_create(
                    repository=repository,
                    year=week_data['year'],
                    week=week_data['week'],
                    defaults={
                        'month': month,
                        'month_name': month_name,
                        'quarter': quarter,
                        'week_start_date': week_data['week_start_date'],
                        'week_end_date': week_data['week_end_date'],
                        'commit_count': week_data['commit_count'],
                        'lines_added': week_data.get('lines_added', 0),
                        'lines_deleted': week_data.get('lines_deleted', 0),
                        'files_changed': week_data.get('files_changed', 0),
                    }
                )
                
                # Update existing record if commit count changed
                if not created and commit_week.commit_count != week_data['commit_count']:
                    commit_week.commit_count = week_data['commit_count']
                    # Also update month metadata in case of edge cases
                    commit_week.month = month
                    commit_week.month_name = month_name
                    commit_week.quarter = quarter
                    commit_week.save()
                    weeks_created += 1
                elif created:
                    weeks_created += 1
        
        return weeks_created
    
    def sync_commits_only(self, github_service, username, force_update, repo_limit):
        """Enhanced commit sync that also handles weekly data for system repos."""
        self.stdout.write('Syncing commit data for existing repositories...')
        
        # Get repositories that need commit sync
        repos_to_sync = GitHubRepository.objects.filter(
            Q(commits_last_synced__isnull=True) |
            Q(commits_last_synced__lt=timezone.now() - timedelta(hours=6))
        ).order_by('-github_updated_at')[:repo_limit]
        
        if force_update:
            repos_to_sync = GitHubRepository.objects.all()[:repo_limit]
        
        commit_sync_count = 0
        weekly_sync_count = 0
        
        for repo in repos_to_sync:
            try:
                self.stdout.write(f'  → Syncing commits for {repo.name}...')
                
                # Sync basic commit stats (existing functionality)
                commit_stats = github_service.sync_repository_commits(username, repo.name)
                
                if commit_stats:
                    # Update repository with commit data (existing logic)
                    repo.total_commits = commit_stats.get('total_commits', 0)
                    repo.last_commit_date = commit_stats.get('last_commit_date')
                    repo.last_commit_sha = commit_stats.get('last_commit_sha', '')
                    repo.last_commit_message = commit_stats.get('last_commit_message', '')
                    repo.commits_last_30_days = commit_stats.get('commits_last_30_days', 0)
                    repo.commits_last_year = commit_stats.get('commits_last_year', 0)
                    repo.avg_commits_per_month = commit_stats.get('avg_commits_per_month', 0.0)
                    repo.commits_last_synced = timezone.now()
                    
                    # Enable detailed tracking for system-linked repos
                    if repo.should_track_detailed_commits():
                        repo.enable_detailed_tracking = True
                    
                    repo.save()
                    commit_sync_count += 1
                    
                    self.stdout.write(
                        f'    ✓ {commit_stats["total_commits"]} commits, {commit_stats["commits_last_30_days"]} in last 30 days'
                    )
                    
                    # If this is a system-linked repo, also sync weekly data
                    if repo.should_track_detailed_commits():
                        try:
                            self.stdout.write('    → Syncing weekly data...')
                            weekly_result = github_service.sync_repository_weekly_commits(
                                username, repo.name, repo.stats_etag
                            )
                            
                            if weekly_result['status'] == 'success':
                                repo.stats_etag = weekly_result['etag']
                                repo.commit_weeks_last_synced = timezone.now()
                                repo.save()
                                
                                weeks_stored = self.store_weekly_commit_data(repo, weekly_result['weekly_data'])
                                weekly_sync_count += 1
                                
                                self.stdout.write(
                                    f'      ✓ {weeks_stored} weeks of detailed data'
                                )
                        except Exception as e:
                            self.stdout.write(
                                self.style.WARNING(f'      ! Weekly sync failed: {e}')
                            )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'    ! No commit data available for {repo.name}')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'    ! Failed to sync commits for {repo.name}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Enhanced commit sync completed:\n'
                f'  ✓ {commit_sync_count} repositories updated\n'
                f'  ✓ {weekly_sync_count} with detailed weekly data'
            )
        )
    
    def sync_full_data(self, github_service, username, force_update, repo_limit, system_repos_only):
        """Enhanced full sync with weekly data integration."""
        
        if system_repos_only:
            self.stdout.write('Syncing system-linked repositories only...')
            # Get existing system-linked repos to update
            existing_repos = GitHubRepository.objects.with_detailed_tracking()
            
            synced_count = 0
            weekly_sync_count = 0
            
            for repo in existing_repos:
                try:
                    self.stdout.write(f'  → Syncing system repo: {repo.name}...')
                    
                    # Get fresh data from GitHub API for this repo
                    repo_data = github_service.get_repository_details(username, repo.name)
                    
                    # Update basic repository data
                    repo.description = repo_data.get('description', '')
                    repo.stars_count = repo_data['stargazers_count']
                    repo.forks_count = repo_data['forks_count']
                    repo.watchers_count = repo_data['watchers_count']
                    repo.size = repo_data['size']
                    repo.language = repo_data.get('language', '')
                    repo.is_private = repo_data['private']
                    repo.is_archived = repo_data['archived']
                    repo.github_updated_at = repo_data['updated_at']
                    repo.save()
                    
                    synced_count += 1
                    self.stdout.write('    ✓ Updated basic repo data')
                    
                    # Sync commits and weekly data
                    commit_success = self.sync_repository_commits(
                        github_service, username, repo.name, repo
                    )
                    
                    if commit_success:
                        # Sync weekly data
                        weekly_success = self.sync_repository_weekly_data(
                            github_service, username, repo.name, repo
                        )
                        if weekly_success:
                            weekly_sync_count += 1
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'    ! Failed to sync {repo.name}: {e}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'System repos sync completed:\n'
                    f'  ✓ {synced_count} repositories updated\n'
                    f'  ✓ {weekly_sync_count} with weekly data synced'
                )
            )
            return
        else:
            # Original full sync logic with enhancements
            self.stdout.write(f'Syncing GitHub data for user: {username}')
            
            # Get repositories from GitHub
            repositories = github_service.get_repositories(username, per_page=100)
            
            synced_count = 0
            updated_count = 0
            commit_sync_count = 0
            weekly_sync_count = 0
            
            for i, repo_data in enumerate(repositories):
                if i >= repo_limit:
                    self.stdout.write(f'  → Reached repository limit ({repo_limit}), stopping...')
                    break
                
                # Sync basic repository data (existing logic with weekly enhancement)
                github_repo, created = GitHubRepository.objects.get_or_create(
                    github_id=repo_data['id'],
                    defaults={
                        'name': repo_data['name'],
                        'full_name': repo_data['full_name'],
                        'description': repo_data.get('description', ''),
                        'html_url': repo_data['html_url'],
                        'clone_url': repo_data['clone_url'],
                        'homepage': repo_data.get('homepage', ''),
                        'stars_count': repo_data['stargazers_count'],
                        'forks_count': repo_data['forks_count'],
                        'watchers_count': repo_data['watchers_count'],
                        'size': repo_data['size'],
                        'language': repo_data.get('language', ''),
                        'is_private': repo_data['private'],
                        'is_fork': repo_data['fork'],
                        'is_archived': repo_data['archived'],
                        'github_created_at': repo_data['created_at'],
                        'github_updated_at': repo_data['updated_at'],
                    }
                )
                
                if created:
                    synced_count += 1
                    self.stdout.write(f'  + Created: {repo_data["full_name"]}')
                elif force_update or github_repo.last_synced < timezone.now() - timezone.timedelta(hours=1):
                    # Update existing repository
                    github_repo.description = repo_data.get('description', '')
                    github_repo.stars_count = repo_data['stargazers_count']
                    github_repo.forks_count = repo_data['forks_count']
                    github_repo.watchers_count = repo_data['watchers_count']
                    github_repo.size = repo_data['size']
                    github_repo.language = repo_data.get('language', '')
                    github_repo.is_private = repo_data['private']
                    github_repo.is_archived = repo_data['archived']
                    github_repo.github_updated_at = repo_data['updated_at']
                    github_repo.save()
                    updated_count += 1
                    self.stdout.write(f'  ↻ Updated: {repo_data["full_name"]}')
                
                # Enhanced commit sync with weekly data for system repos
                if not github_repo.is_archived and not github_repo.is_fork:
                    should_sync_commits = (
                        created or 
                        force_update or 
                        not github_repo.commits_last_synced or
                        github_repo.commits_last_synced < timezone.now() - timedelta(hours=6)
                    )
                    
                    if should_sync_commits:
                        # Standard commit sync
                        commit_success = self.sync_repository_commits(
                            github_service, username, repo_data['name'], github_repo
                        )
                        
                        if commit_success:
                            commit_sync_count += 1
                            
                            # If system-linked, also sync weekly data
                            if github_repo.should_track_detailed_commits():
                                weekly_success = self.sync_repository_weekly_data(
                                    github_service, username, repo_data['name'], github_repo
                                )
                                if weekly_success:
                                    weekly_sync_count += 1
                
                # Language sync (existing logic)
                if created or force_update:
                    self.sync_repository_languages(github_service, username, repo_data['name'], github_repo)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Full GitHub sync completed:\n'
                    f'  ✓ {synced_count} created, {updated_count} updated\n'
                    f'  ✓ {commit_sync_count} commit syncs\n'
                    f'  ✓ {weekly_sync_count} weekly data syncs'
                )
            )
    
    def sync_repository_commits(self, github_service, username, repo_name, github_repo):
        """Sync basic commit data for a repository."""
        try:
            self.stdout.write(f'    → Syncing commits for {repo_name}...')
            
            commit_stats = github_service.sync_repository_commits(username, repo_name)
            
            if commit_stats:
                github_repo.total_commits = commit_stats.get('total_commits', 0)
                github_repo.last_commit_date = commit_stats.get('last_commit_date')
                github_repo.last_commit_sha = commit_stats.get('last_commit_sha', '')
                github_repo.last_commit_message = commit_stats.get('last_commit_message', '')
                github_repo.commits_last_30_days = commit_stats.get('commits_last_30_days', 0)
                github_repo.commits_last_year = commit_stats.get('commits_last_year', 0)
                github_repo.avg_commits_per_month = commit_stats.get('avg_commits_per_month', 0.0)
                github_repo.commits_last_synced = timezone.now()
                
                # Enable detailed tracking for system repos
                if github_repo.should_track_detailed_commits():
                    github_repo.enable_detailed_tracking = True
                
                github_repo.save()
                
                self.stdout.write(
                    f'      ✓ {commit_stats["total_commits"]} total, {commit_stats["commits_last_30_days"]} recent'
                )
                return True
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'      ! Commit sync failed: {e}')
            )
        return False
    
    def sync_repository_weekly_data(self, github_service, username, repo_name, github_repo):
        """Sync weekly commit data for a system-linked repository."""
        try:
            self.stdout.write('      → Syncing weekly data...')
            
            result = github_service.sync_repository_weekly_commits(
                username, repo_name, github_repo.stats_etag
            )
            
            if result['status'] == 'success':
                github_repo.stats_etag = result['etag']
                github_repo.commit_weeks_last_synced = timezone.now()
                github_repo.save()
                
                weeks_stored = self.store_weekly_commit_data(github_repo, result['weekly_data'])
                
                self.stdout.write(
                    f'        ✓ {weeks_stored} weeks of data'
                )
                return True
            elif result['status'] == 'computing':
                self.stdout.write(
                    '        ⏳ GitHub computing (will retry later)'
                )
            elif result['status'] == 'not_modified':
                github_repo.commit_weeks_last_synced = timezone.now()
                github_repo.save()
                self.stdout.write(
                    '        ≈ No changes'
                )
                return True
                
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'        ! Weekly sync failed: {e}')
            )
        return False
    
    def sync_repository_languages(self, github_service, username, repo_name, github_repo):
        """Sync language data for a repository."""
        try:
            languages_data = github_service.get_repository_languages(username, repo_name)

            # Clear existing language data
            github_repo.languages.all().delete()

            # Calculate total bytes for percentage calculation
            total_bytes = sum(languages_data.values()) if languages_data else 0

            # Create new language records
            for language, bytes_count in languages_data.items():
                percentage = (bytes_count / total_bytes * 100) if total_bytes > 0 else 0
                GitHubLanguage.objects.create(
                    repository=github_repo,
                    language=language,
                    bytes_count=bytes_count,
                    percentage=percentage
                )
        except GitHubAPIError as e:
            self.stdout.write(
                self.style.WARNING(f'      ! Language sync failed: {e}')
            )
