from django.core.management.base import BaseCommand
from django.utils import timezone
from core.services.github_api import GitHubAPIService, GitHubAPIError
from projects.models import GitHubRepository, GitHubLanguage
import logging

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
    
    def handle(self, *args, **options):
        github_service = GitHubAPIService()
        username = options.get('username') or github_service.username
        force_update = options.get('force', False)

        if not username:
            self.stdout.write(
                self.style.ERROR('No GitHub username configured or provided')
            )
            return
        try:
            self.stdout.write(f'Syncing GitHub data for user {username}')

            # Get repositories from GitHub
            repositories = github_service.get_repositories(username, per_page=100)

            synced_count = 0
            updated_count = 0

            for repo_data in repositories:
                # Check if repo already exists
                github_repo, created = GitHubRepository.objects.get_or_create(
                    github_id=repo_data['id'],
                    defaults={
                        'name': repo_data['name'],
                        'full_name': repo_data['full_name'],
                        'description': repo_data['description'],
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
                    # Update existing repo
                    github_repo.description = repo_data.get('description', '')
                    github_repo.stars_count = repo_data['stargazers_count']
                    github_repo.forks_count = repo_data['forks_count']
                    github_repo.watchers_count = repo_data['watchers_count']
                    github_repo.size = repo_data['size']
                    github_repo.language = repo_data.get('language', '')
                    github_repo.is_archived = repo_data['archived']
                    github_repo.github_updated_at = repo_data['updated_at']
                    github_repo.save()
                    updated_count += 1
                    self.stdout.write(f'  ↻ Updated: {repo_data["full_name"]}')
                
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
                    self.style.SUCCESS(f'GitHub sync completed: {synced_count} created, {updated_count} updated')
                )
        except GitHubAPIError as e:
            self.stdout.write(
                self.style.ERROR(f"GitHub API error: {e}")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Unexpected error: {e}")
            )
