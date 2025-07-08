from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from core.services.github_api import GitHubAPIService, GitHubAPIError
from projects.models import GitHubRepository, GitHubLanguage
import logging
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync GitHub repository data with local database'

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
            '--limit-repos',
            type=int,
            default=20,
            help='Limit number of repos to sync commits for (to avoid rate limits)',
        )
    
    def handle(self, *args, **options):
        github_service = GitHubAPIService()
        username = options.get('username') or github_service.username
        force_update = options.get('force', False)
        commits_only = options.get('commits_only', False)
        repo_limit = options.get('limit_repos', 20)

        if not username:
            self.stdout.write(
                self.style.ERROR('No GitHub username configured or provided')
            )
            return
        
        try:
            if commits_only:
                self.sync_commits_only(github_service, username, force_update, repo_limit)
            else:
                self.sync_full_data(github_service, username, force_update, repo_limit)
            # self.stdout.write(f'Syncing GitHub data for user {username}')

            # # Get repositories from GitHub
            # repositories = github_service.get_repositories(username, per_page=100)

            # synced_count = 0
            # updated_count = 0

            # for repo_data in repositories:
            #     # Check if repo already exists
            #     github_repo, created = GitHubRepository.objects.get_or_create(
            #         github_id=repo_data['id'],
            #         defaults={
            #             'name': repo_data['name'],
            #             'full_name': repo_data['full_name'],
            #             'description': repo_data['description'],
            #             'html_url': repo_data['html_url'],
            #             'clone_url': repo_data['clone_url'],
            #             'homepage': repo_data.get('homepage', ''),
            #             'stars_count': repo_data['stargazers_count'],
            #             'forks_count': repo_data['forks_count'],
            #             'watchers_count': repo_data['watchers_count'],
            #             'size': repo_data['size'],
            #             'language': repo_data.get('language', ''),
            #             'is_private': repo_data['private'],
            #             'is_fork': repo_data['fork'],
            #             'is_archived': repo_data['archived'],
            #             'github_created_at': repo_data['created_at'],
            #             'github_updated_at': repo_data['updated_at'],
            #         }
            #     )

            #     if created:
            #         synced_count += 1
            #         self.stdout.write(f'  + Created: {repo_data["full_name"]}')
            #     elif force_update or github_repo.last_synced < timezone.now() - timezone.timedelta(hours=1):
            #         # Update existing repo
            #         github_repo.description = repo_data.get('description', '')
            #         github_repo.stars_count = repo_data['stargazers_count']
            #         github_repo.forks_count = repo_data['forks_count']
            #         github_repo.watchers_count = repo_data['watchers_count']
            #         github_repo.size = repo_data['size']
            #         github_repo.language = repo_data.get('language', '')
            #         github_repo.is_archived = repo_data['archived']
            #         github_repo.github_updated_at = repo_data['updated_at']
            #         github_repo.save()
            #         updated_count += 1
            #         self.stdout.write(f'  ↻ Updated: {repo_data["full_name"]}')
                
            #     # Sync language data (for created or recently updated repos)
            #     if created or force_update:
            #         try:
            #             languages_data = github_service.get_repository_languages(username, repo_data['name'])

            #             # Clear existing language data
            #             github_repo.languages.all().delete()

            #             # Calculate total bytes for percentage calculation
            #             total_bytes = sum(languages_data.values()) if languages_data else 0

            #             # Create new language records
            #             for language, bytes_count in languages_data.items():
            #                 percentage = (bytes_count / total_bytes * 100) if total_bytes > 0 else 0
            #                 GitHubLanguage.objects.create(
            #                     repository=github_repo,
            #                     language=language,
            #                     bytes_count=bytes_count,
            #                     percentage=percentage
            #                 )
            #         except GitHubAPIError as e:
            #             self.stdout.write(
            #                 self.style.WARNING(f'  ! Could not sync langues for {repo_data["name"]}: {e}')
            #             )
            #     self.stdout.write(
            #         self.style.SUCCESS(f'GitHub sync completed: {synced_count} created, {updated_count} updated')
            #     )
        except GitHubAPIError as e:
            self.stdout.write(
                self.style.ERROR(f'GitHub API error: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error: {e}')
            )
    
    def sync_commits_only(self, github_service, username, force_update, repo_limit):
        """Sync only commit data for existing repositories."""
        self.stdout.write(f'Syncing commit data for existing repositories...')
        
        # Get repositories that need commit sync
        repos_to_sync = GitHubRepository.objects.filter(
            Q(commits_last_synced__isnull=True) |
            Q(commits_last_synced__lt=timezone.now() - timedelta(hours=6))
        ).order_by('-github_updated_at')[:repo_limit]
        
        if force_update:
            repos_to_sync = GitHubRepository.objects.all()[:repo_limit]
        
        commit_sync_count = 0
        
        for repo in repos_to_sync:
            try:
                self.stdout.write(f'  → Syncing commits for {repo.name}...')
                
                commit_stats = github_service.sync_repository_commits(username, repo.name)
                
                if commit_stats:
                    # Update repository with commit data
                    repo.total_commits = commit_stats.get('total_commits', 0)
                    repo.last_commit_date = commit_stats.get('last_commit_date')
                    repo.last_commit_sha = commit_stats.get('last_commit_sha', '')
                    repo.last_commit_message = commit_stats.get('last_commit_message', '')
                    repo.last_commit_author = commit_stats.get('last_commit_author', '')
                    repo.commits_last_30_days = commit_stats.get('commits_last_30_days', 0)
                    repo.commits_last_year = commit_stats.get('commits_last_year', 0)
                    repo.avg_commits_per_month = commit_stats.get('avg_commits_per_month', 0.0)
                    repo.commits_last_synced = timezone.now()
                    
                    repo.save()
                    commit_sync_count += 1
                    
                    self.stdout.write(
                        f'    ✓ Synced {commit_stats["total_commits"]} commits'
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
                f'Commit sync completed: {commit_sync_count} repositories updated'
            )
        )
    
    def sync_full_data(self, github_service, username, force_update, repo_limit):
        """Sync full repository data including commits."""
        self.stdout.write(f'Syncing GitHub data for user: {username}')
        
        # Get repositories from GitHub
        repositories = github_service.get_repositories(username, per_page=100)
        
        synced_count = 0
        updated_count = 0
        commit_sync_count = 0
        
        for i, repo_data in enumerate(repositories):
            if i >= repo_limit:
                self.stdout.write(f'  → Reached repository limit ({repo_limit}), stopping commit sync...')
                break
                
            # Sync basic repository data (existing logic)
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
            
            # Sync commit data if repository is not archived and not a fork
            if not github_repo.is_archived and not github_repo.is_fork:
                needs_commit_sync = (
                    created or 
                    force_update or 
                    not github_repo.commits_last_synced or
                    github_repo.commits_last_synced < timezone.now() - timedelta(hours=6)
                )
                
                if needs_commit_sync:
                    try:
                        self.stdout.write(f'    → Syncing commits for {repo_data["name"]}...')
                        
                        commit_stats = github_service.sync_repository_commits(username, repo_data['name'])
                        
                        if commit_stats:
                            github_repo.total_commits = commit_stats.get('total_commits', 0)
                            github_repo.last_commit_date = commit_stats.get('last_commit_date')
                            github_repo.last_commit_sha = commit_stats.get('last_commit_sha', '')
                            github_repo.last_commit_message = commit_stats.get('last_commit_message', '')
                            github_repo.commits_last_30_days = commit_stats.get('commits_last_30_days', 0)
                            github_repo.commits_last_year = commit_stats.get('commits_last_year', 0)
                            github_repo.avg_commits_per_month = commit_stats.get('avg_commits_per_month', 0.0)
                            github_repo.commits_last_synced = timezone.now()
                            
                            github_repo.save()
                            commit_sync_count += 1
                            
                            self.stdout.write(
                                f'      ✓ {commit_stats["total_commits"]} commits, {commit_stats["commits_last_30_days"]} in last 30 days'
                            )
                    
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'      ! Could not sync commits for {repo_data["name"]}: {e}')
                        )

            # Sync language data (for created or recently updated repos)
            if created or force_update:
                try:
                    languages_data = github_service.get_repository_languages(username, repo_data['name'])

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
                        self.style.WARNING(f'  ! Could not sync langues for {repo_data["name"]}: {e}')
                    )
        self.stdout.write(
            self.style.SUCCESS(
                f'GitHub sync completed: {synced_count} created, {updated_count} updated, {commit_sync_count} commit syncs'
            )
        )