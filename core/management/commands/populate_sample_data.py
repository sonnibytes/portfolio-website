"""
Django Management Command to Populate Sample Data
File: core/management/commands/populate_sample_data.py

Creates comprehensive sample data across all apps:
- Core: Pages, Skills, Education, Experience, Contacts, Social Links
- Blog: Categories, Tags, Posts, Comments, Series, System Connections  
- Projects: Technologies, Systems, Features, GitHub repos, Architecture

NOTE TO SELF: Commented out any GitHub models, can populate those with sync command. Also removed imports for these in case I missed one.
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from datetime import datetime, date, timedelta
from random import randint, choice, sample
from faker import Faker
import random

# Import all models
from core.models import (
    CorePage, Skill, Education, EducationSkillDevelopment, 
    Experience, Contact, SocialLink, PortfolioAnalytics, 
    SkillTechnologyRelation
)
from blog.models import (
    Category, Tag, Post, Comment, PostView, Series, 
    SeriesPost, SystemLogEntry
)
from projects.models import (
    Technology, SystemModule, SystemImage, SystemFeature,
    SystemSkillGain, LearningMilestone, ArchitectureComponent,
    ArchitectureConnection
)

fake = Faker()

class Command(BaseCommand):
    help = 'Populate the database with comprehensive sample data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )
        parser.add_argument(
            '--users',
            type=int,
            default=1,
            help='Number of users to create (default: 1)',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        self.stdout.write('Starting data population...')
        
        # Create users first
        self.users = self.create_users(options['users'])
        
        # Core app data
        self.create_core_pages()
        self.skills = self.create_skills()
        self.technologies = self.create_technologies()  # From projects app
        self.create_skill_technology_relations()
        self.educations = self.create_education()
        self.create_education_skill_development()
        self.create_experience()
        self.create_social_links()
        self.create_contacts()
        
        # Projects app data
        self.systems = self.create_systems()
        self.create_system_features()
        self.create_system_images()
        self.create_github_repos()
        self.create_system_commit_data()
        self.create_learning_milestones()
        self.create_architecture_components()
        self.create_architecture_connections()
        
        # Blog app data  
        self.categories = self.create_blog_categories()
        self.tags = self.create_blog_tags()
        self.posts = self.create_blog_posts()
        self.create_comments()
        self.create_post_views()
        self.series = self.create_blog_series()
        self.create_series_posts()
        self.create_system_log_entries()
        
        # Analytics
        self.create_portfolio_analytics()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample data!')
        )

    def clear_data(self):
        """Clear existing data in reverse dependency order"""
        # Clear through models first
        SystemLogEntry.objects.all().delete()
        SeriesPost.objects.all().delete()
        EducationSkillDevelopment.objects.all().delete()
        SkillTechnologyRelation.objects.all().delete()
        ArchitectureConnection.objects.all().delete()
        
        # Clear dependent models
        Comment.objects.all().delete()
        PostView.objects.all().delete()
        SystemFeature.objects.all().delete()
        SystemImage.objects.all().delete()
        SystemSkillGain.objects.all().delete()
        # GitHubCommitWeek.objects.all().delete()
        # SystemCommitData.objects.all().delete()
        LearningMilestone.objects.all().delete()
        ArchitectureComponent.objects.all().delete()
        
        # Clear main models
        Post.objects.all().delete()
        Series.objects.all().delete()
        SystemModule.objects.all().delete()
        # GitHubRepository.objects.all().delete()
        Contact.objects.all().delete()
        Experience.objects.all().delete()
        Education.objects.all().delete()
        
        # Clear base models
        Tag.objects.all().delete()
        Category.objects.all().delete()
        Technology.objects.all().delete()
        Skill.objects.all().delete()
        SocialLink.objects.all().delete()
        CorePage.objects.all().delete()
        PortfolioAnalytics.objects.all().delete()
        
        self.stdout.write('Data cleared.')

    def create_users(self, count):
        """Create test users"""
        users = []
        # Create superuser if doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Portfolio',
                last_name='Admin'
            )
            users.append(admin)
            self.stdout.write(f'Created superuser: admin/admin123')
        else:
            users.append(User.objects.get(username='admin'))
            
        # Create additional test users
        for i in range(count - 1):
            user = User.objects.create_user(
                username=f'testuser{i+1}',
                email=fake.email(),
                password='testpass123',
                first_name=fake.first_name(),
                last_name=fake.last_name()
            )
            users.append(user)
            
        self.stdout.write(f'Created {len(users)} users')
        return users

    def create_core_pages(self):
        """Create core static pages"""
        pages_data = [
            {
                'title': 'Privacy Policy',
                'content': fake.text(2000),
            },
            {
                'title': 'Terms of Service', 
                'content': fake.text(1500),
            },
            {
                'title': 'About This Site',
                'content': fake.text(1200),
            }
        ]
        
        for page_data in pages_data:
            page, created = CorePage.objects.get_or_create(
                title=page_data['title'],
                defaults={
                    'slug': slugify(page_data['title']),
                    'content': page_data['content'],
                    'meta_description': fake.sentence(10),
                    'is_published': True
                }
            )
            if created:
                self.stdout.write(f'Created page: {page.title}')

    def create_skills(self):
        """Create programming and technical skills"""
        skills_data = [
             # Actual Skill w new model rework
             # Technical Concepts
            {'name': 'Machine Learning', 'category': 'technical_concept', 'color': '#FFBD2E', 'icon': 'fas fa-brain', 'proficiency': 5, 'featured': True, 'certified': True},
            {'name': 'API Design', 'category': 'methodology', 'color': '#00FFFF', 'icon': 'fas fa-puzzle-piece', 'proficiency': 4, 'featured': True, 'certified': False},
            {'name': 'Database Design', 'category': 'methodology', 'color': '#336791', 'icon': 'fas fa-database', 'proficiency': 3, 'featured': False, 'certified': False},
            {'name': 'Data Science', 'category': 'domain_knowledge', 'color': '#37b24d', 'icon': 'fas fa-vials', 'proficiency': 4, 'featured': True, 'certified': True},
            {'name': 'Web Development', 'category': 'technical_concept', 'color': '#FF8A80', 'icon': 'fas fa-globe', 'proficiency': 4, 'featured': False, 'certified': False},
            {'name': 'GUI Development', 'category': 'technical_concept', 'color': '#B39DDB', 'icon': 'fas fa-laptop-code', 'proficiency': 2, 'featured': False, 'certified': False, 'learning': True},
            
            # Methodology/Process
            {'name': 'Problem Solving', 'category': 'soft_skill', 'color': '#FFBD2E', 'icon': 'fas fa-brain', 'proficiency': 5, 'featured': True, 'certified': True},
            {'name': 'Debugging', 'category': 'methodology', 'color': '#00FFFF', 'icon': 'fas fa-puzzle-piece', 'proficiency': 4, 'featured': True, 'certified': False},
            {'name': 'Database Design', 'category': 'methodology', 'color': '#336791', 'icon': 'fas fa-database', 'proficiency': 3, 'featured': False, 'certified': False},
            {'name': 'Data Science', 'category': 'domain_knowledge', 'color': '#37b24d', 'icon': 'fas fa-vials', 'proficiency': 4, 'featured': True, 'certified': True},
            {'name': 'Web Development', 'category': 'technical_concept', 'color': '#FF8A80', 'icon': 'fas fa-globe', 'proficiency': 4, 'featured': False, 'certified': False},
            {'name': 'GUI Development', 'category': 'technical_concept', 'color': '#B39DDB', 'icon': 'fas fa-laptop-code', 'proficiency': 2, 'featured': False, 'certified': False, 'learning': True}, 

            # Soft Skills
            {'name': 'Problem Solving', 'category': 'soft_skill', 'color': '#FFBD2E', 'icon': 'fas fa-brain', 'proficiency': 5, 'featured': True, 'certified': True},
            {'name': 'Debugging', 'category': 'methodology', 'color': '#00FFFF', 'icon': 'fas fa-puzzle-piece', 'proficiency': 4, 'featured': True, 'certified': False},
            {'name': 'Database Design', 'category': 'methodology', 'color': '#336791', 'icon': 'fas fa-database', 'proficiency': 3, 'featured': False, 'certified': False},
            {'name': 'Data Science', 'category': 'domain_knowledge', 'color': '#37b24d', 'icon': 'fas fa-vials', 'proficiency': 4, 'featured': True, 'certified': True},
            {'name': 'Web Development', 'category': 'technical_concept', 'color': '#FF8A80', 'icon': 'fas fa-globe', 'proficiency': 4, 'featured': False, 'certified': False},
            {'name': 'GUI Development', 'category': 'technical_concept', 'color': '#B39DDB', 'icon': 'fas fa-laptop-code', 'proficiency': 2, 'featured': False, 'certified': False, 'learning': True}, 

            # Domain Knowledge
            {'name': 'Problem Solving', 'category': 'soft_skill', 'color': '#FFBD2E', 'icon': 'fas fa-brain', 'proficiency': 5, 'featured': True, 'certified': True},
            {'name': 'Debugging', 'category': 'methodology', 'color': '#00FFFF', 'icon': 'fas fa-puzzle-piece', 'proficiency': 4, 'featured': True, 'certified': False},
            {'name': 'Database Design', 'category': 'methodology', 'color': '#336791', 'icon': 'fas fa-database', 'proficiency': 3, 'featured': False, 'certified': False},
            {'name': 'Data Science', 'category': 'domain_knowledge', 'color': '#37b24d', 'icon': 'fas fa-vials', 'proficiency': 4, 'featured': True, 'certified': True},
            {'name': 'Web Development', 'category': 'technical_concept', 'color': '#FF8A80', 'icon': 'fas fa-globe', 'proficiency': 4, 'featured': False, 'certified': False},
            {'name': 'GUI Development', 'category': 'technical_concept', 'color': '#B39DDB', 'icon': 'fas fa-laptop-code', 'proficiency': 2, 'featured': False, 'certified': False, 'learning': True}, 

            # Other
            {'name': 'Problem Solving', 'category': 'soft_skill', 'color': '#FFBD2E', 'icon': 'fas fa-brain', 'proficiency': 5, 'featured': True, 'certified': True},
            {'name': 'Debugging', 'category': 'methodology', 'color': '#00FFFF', 'icon': 'fas fa-puzzle-piece', 'proficiency': 4, 'featured': True, 'certified': False},
            {'name': 'Database Design', 'category': 'methodology', 'color': '#336791', 'icon': 'fas fa-database', 'proficiency': 3, 'featured': False, 'certified': False},
            {'name': 'Data Science', 'category': 'domain_knowledge', 'color': '#37b24d', 'icon': 'fas fa-vials', 'proficiency': 4, 'featured': True, 'certified': True},
            {'name': 'Web Development', 'category': 'technical_concept', 'color': '#FF8A80', 'icon': 'fas fa-globe', 'proficiency': 4, 'featured': False, 'certified': False},
            {'name': 'GUI Development', 'category': 'technical_concept', 'color': '#B39DDB', 'icon': 'fas fa-laptop-code', 'proficiency': 2, 'featured': False, 'certified': False, 'learning': True},     
            ### WITH REWORK, ALL THESE WOULD BE TECHNOLOGIES
            # # Programming Languages
            # {'name': 'Python', 'category': 'language', 'proficiency': 5, 'featured': True, 'certified': True},
            # {'name': 'JavaScript', 'category': 'language', 'proficiency': 4, 'featured': True, 'certified': False},
            # {'name': 'TypeScript', 'category': 'language', 'proficiency': 3, 'featured': False, 'certified': False},
            # {'name': 'SQL', 'category': 'language', 'proficiency': 4, 'featured': True, 'certified': True},
            # {'name': 'HTML/CSS', 'category': 'language', 'proficiency': 4, 'featured': False, 'certified': False},
            # {'name': 'Rust', 'category': 'language', 'proficiency': 2, 'featured': False, 'certified': False, 'learning': True},
            
            # # Frameworks
            # {'name': 'Django', 'category': 'framework', 'proficiency': 5, 'featured': True, 'certified': False},
            # {'name': 'FastAPI', 'category': 'framework', 'proficiency': 4, 'featured': True, 'certified': False},
            # {'name': 'React', 'category': 'framework', 'proficiency': 3, 'featured': False, 'certified': False},
            # {'name': 'Vue.js', 'category': 'framework', 'proficiency': 2, 'featured': False, 'certified': False, 'learning': True},
            
            # # Tools & Technologies
            # {'name': 'Docker', 'category': 'tool', 'proficiency': 4, 'featured': True, 'certified': True},
            # {'name': 'PostgreSQL', 'category': 'database', 'proficiency': 4, 'featured': True, 'certified': False},
            # {'name': 'Redis', 'category': 'database', 'proficiency': 3, 'featured': False, 'certified': False},
            # {'name': 'Git', 'category': 'tool', 'proficiency': 5, 'featured': False, 'certified': False},
            # {'name': 'AWS', 'category': 'cloud', 'proficiency': 3, 'featured': True, 'certified': True},
            # {'name': 'Linux', 'category': 'tool', 'proficiency': 4, 'featured': False, 'certified': False},
            
            # # Data Science
            # {'name': 'Pandas', 'category': 'library', 'proficiency': 4, 'featured': True, 'certified': False},
            # {'name': 'NumPy', 'category': 'library', 'proficiency': 4, 'featured': False, 'certified': False},
            # {'name': 'Matplotlib', 'category': 'library', 'proficiency': 3, 'featured': False, 'certified': False},
            # {'name': 'Scikit-learn', 'category': 'library', 'proficiency': 3, 'featured': False, 'certified': False},
        ]
        
        skills = []
        for skill_data in skills_data:
            skill, created = Skill.objects.get_or_create(
                name=skill_data['name'],
                defaults={
                    'slug': slugify(skill_data['name']),
                    'category': skill_data['category'],
                    'icon': skill_data['icon'],
                    'color': skill_data['color'],
                    'proficiency': skill_data['proficiency'],
                    'is_featured': skill_data.get('featured', False),
                    'is_certified': skill_data.get('certified', False),
                    'is_currently_learning': skill_data.get('learning', False),
                    'description': fake.text(200),
                    'years_experience': randint(1, 8),
                    'first_used': fake.date_between(start_date='-8y', end_date='today'),
                    'last_used': fake.date_between(start_date='-1y', end_date='today'),
                }
            )
            skills.append(skill)
            if created:
                self.stdout.write(f'Created skill: {skill.name}')
                
        self.stdout.write(f'Created {len(skills)} skills')
        return skills

    def create_technologies(self):
        """Create technologies from projects app"""
        tech_data = [
            # Programming Languages
            {'name': 'Python', 'category': 'language', 'color': '#3776ab', 'icon': 'fab fa-python'},
            {'name': 'JavaScript', 'category': 'language', 'color': '#f7df1e', 'icon': 'fab fa-js-square'},
            {'name': 'SQL', 'category': 'language', 'color': '#336791', 'icon': 'fas fa-database'},
            {'name': 'HTML/CSS', 'category': 'language', 'color': '#37b24d', 'icon': 'fab fa-html5'},
            {'name': 'Rust', 'category': 'language', 'color': '#dc382d', 'icon': 'fab fa-rust'},
            
            # Frameworks
            {'name': 'Django', 'category': 'framework', 'color': '#092e20', 'icon': 'fas fa-server'},
            {'name': 'FastAPI', 'category': 'framework', 'color': '#336791', 'icon': 'fas fa-code'},
            {'name': 'React', 'category': 'framework', 'color': '#61dafb', 'icon': 'fab fa-react'},
            {'name': 'Vue.js', 'category': 'framework', 'color': '#37b24d', 'icon': 'fab fa-vuejs'},
            
            # Tools & Technologies
            {'name': 'Docker', 'category': 'tool', 'color': '#2496ed', 'icon': 'fab fa-docker'},
            {'name': 'PostgreSQL', 'category': 'database', 'color': '#336791', 'icon': 'fas fa-database'},
            {'name': 'Redis', 'category': 'database', 'color': '#dc382d', 'icon': 'fas fa-database'},
            {'name': 'Git', 'category': 'tool', 'color': '#dc382d', 'icon': 'fab fa-git-alt'},
            {'name': 'AWS', 'category': 'cloud', 'color': '#ff9900', 'icon': 'fab fa-aws'},
            {'name': 'Linux', 'category': 'os', 'color': '#092e20', 'icon': 'fab fa-linux'},
            
            # Data Science
            {'name': 'Pandas', 'category': 'framework', 'color': '#61dafb', 'icon': 'fas fa-chart-bar'},
            {'name': 'NumPy', 'category': 'ai', 'color': '#ff9900', 'icon': 'fas fa-microscope'},
            {'name': 'Matplotlib', 'category': 'framework', 'color': '#336791', 'icon': 'fas fa-chart-line'},
            {'name': 'Scikit-learn', 'category': 'ai', 'color': '#f7df1e', 'icon': 'fas fa-flask'},

        ]
        
        technologies = []
        for tech in tech_data:
            technology, created = Technology.objects.get_or_create(
                name=tech['name'],
                defaults={
                    'slug': slugify(tech['name']),
                    'category': tech['category'],
                    'color': tech['color'],
                    'icon': tech['icon'],
                    'description': fake.text(150)
                }
            )
            technologies.append(technology)
            if created:
                self.stdout.write(f'Created technology: {technology.name}')
                
        self.stdout.write(f'Created {len(technologies)} technologies')
        return technologies

    def create_skill_technology_relations(self):
        """Create relationships between skills and technologies"""
        # TODO: Created w old Skill -> Technology Relationship Logic. Add manually for now.
        # relations_created = 0
        
        # # Map skills to technologies where names match
        # for skill in self.skills:
        #     matching_tech = next((t for t in self.technologies if t.name == skill.name), None)
        #     if matching_tech:
        #         relation, created = SkillTechnologyRelation.objects.get_or_create(
        #             skill=skill,
        #             technology=matching_tech,
        #             defaults={
        #                 'proficiency_gained': randint(1, 3),
        #                 'years_used_together': randint(1, 5),
        #                 'relationship_type': choice(['primary', 'secondary', 'complementary']),
        #                 'notes': fake.sentence(10)
        #             }
        #         )
        #         if created:
        #             relations_created += 1
                    
        # self.stdout.write(f'Created {relations_created} skill-technology relations')
        pass

    def create_education(self):
        """Create education entries"""
        education_data = [
            {
                'degree': 'Bachelor of Science in Computer Science',
                'institution': 'University of Technology',
                'learning_type': 'formal_degree',
                'start_date': date(2018, 8, 15),
                'end_date': date(2022, 5, 15),
                'hours': 2400,
                'current': False
            },
            {
                'degree': 'Python for Data Science Specialization',
                'institution': 'Coursera - University of Michigan',
                'learning_type': 'online_course',
                'start_date': date(2023, 1, 10),
                'end_date': date(2023, 4, 15),
                'hours': 120,
                'current': False
            },
            {
                'degree': 'AWS Solutions Architect Certification',
                'institution': 'Amazon Web Services',
                'learning_type': 'certification',
                'start_date': date(2023, 6, 1),
                'end_date': date(2023, 8, 15),
                'hours': 80,
                'current': False
            },
            {
                'degree': 'Advanced React Development',
                'institution': 'Udemy',
                'learning_type': 'online_course',
                'start_date': date(2024, 1, 1),
                'end_date': None,
                'hours': 40,
                'current': True
            }
        ]
        
        educations = []
        for edu_data in education_data:
            education, created = Education.objects.get_or_create(
                degree=edu_data['degree'],
                institution=edu_data['institution'],
                defaults={
                    'slug': slugify(f"{edu_data['degree']} {edu_data['institution']}"),
                    'description': fake.text(300),
                    'start_date': edu_data['start_date'],
                    'end_date': edu_data['end_date'],
                    'is_current': edu_data['current'],
                    'learning_type': edu_data['learning_type'],
                    'platform': edu_data['institution'],
                    'certificate_url': fake.url() if randint(0, 1) else '',
                    'hours_completed': edu_data['hours'],
                    'learning_intensity': randint(2, 5),
                    'career_relevance': randint(3, 5),
                }
            )
            educations.append(education)
            if created:
                self.stdout.write(f'Created education: {education.degree}')
                
        self.stdout.write(f'Created {len(educations)} education entries')
        return educations

    def create_education_skill_development(self):
        """Create skill development through education"""
        developments_created = 0
        
        for education in self.educations:
            # Randomly assign 3-6 skills per education
            num_skills = randint(3, 6)
            selected_skills = sample(self.skills, min(num_skills, len(self.skills)))
            
            for skill in selected_skills:
                development, created = EducationSkillDevelopment.objects.get_or_create(
                    education=education,
                    skill=skill,
                    defaults={
                        'proficiency_before': randint(0, 2),
                        'proficiency_after': randint(3, 5),
                        'learning_focus': choice(['foundation', 'advanced', 'practical', 'theoretical']),
                        'importance_level': randint(1, 5),
                        'learning_notes': fake.sentence(15)
                    }
                )
                if created:
                    developments_created += 1
                    
        self.stdout.write(f'Created {developments_created} education skill developments')

    def create_experience(self):
        """Create work experience entries"""
        experience_data = [
            {
                'company': 'TechStart Solutions',
                'position': 'Junior Python Developer',
                'location': 'Remote',
                'start_date': date(2022, 6, 1),
                'end_date': date(2023, 8, 15),
                'current': False,
                'technologies': 'Python, Django, PostgreSQL, Docker'
            },
            {
                'company': 'DataFlow Industries',
                'position': 'Backend Developer',
                'location': 'San Francisco, CA',
                'start_date': date(2023, 9, 1),
                'end_date': None,
                'current': True,
                'technologies': 'Python, FastAPI, AWS, Redis, Kubernetes'
            },
            {
                'company': 'Freelance',
                'position': 'Full Stack Developer',
                'location': 'Remote',
                'start_date': date(2021, 1, 1),
                'end_date': date(2022, 5, 31),
                'current': False,
                'technologies': 'Python, Django, JavaScript, React, PostgreSQL'
            }
        ]
        
        for exp_data in experience_data:
            experience, created = Experience.objects.get_or_create(
                company=exp_data['company'],
                position=exp_data['position'],
                defaults={
                    'slug': slugify(f"{exp_data['position']} {exp_data['company']}"),
                    'location': exp_data['location'],
                    'description': fake.text(500),
                    'start_date': exp_data['start_date'],
                    'end_date': exp_data['end_date'],
                    'is_current': exp_data['current'],
                    'technologies': exp_data['technologies'],
                }
            )
            if created:
                self.stdout.write(f'Created experience: {experience.position} at {experience.company}')

    def create_social_links(self):
        """Create social media and profile links"""
        social_data = [
            {
                'platform': 'GitHub',
                'url': 'https://github.com/yourhandle',
                'icon': 'fab fa-github',
                'display_order': 1,
                'featured': True
            },
            {
                'platform': 'LinkedIn', 
                'url': 'https://linkedin.com/in/yourprofile',
                'icon': 'fab fa-linkedin',
                'display_order': 2,
                'featured': True
            },
            {
                'platform': 'Twitter',
                'url': 'https://twitter.com/yourhandle',
                'icon': 'fab fa-twitter', 
                'display_order': 3,
                'featured': False
            },
            {
                'platform': 'Stack Overflow',
                'url': 'https://stackoverflow.com/users/yourprofile',
                'icon': 'fab fa-stack-overflow',
                'display_order': 4,
                'featured': False
            }
        ]
        
        for social in social_data:
            link, created = SocialLink.objects.get_or_create(
                platform=social['platform'],
                defaults={
                    'url': social['url'],
                    'icon_class': social['icon'],
                    'display_order': social['display_order'],
                    'is_featured': social['featured'],
                    'is_active': True,
                    'description': f'My {social["platform"]} profile'
                }
            )
            if created:
                self.stdout.write(f'Created social link: {link.platform}')

    def create_contacts(self):
        """Create sample contact form submissions"""
        inquiry_types = ['project', 'hiring', 'collaboration', 'question', 'feedback']
        priorities = ['low', 'normal', 'high']
        
        for i in range(15):
            contact = Contact.objects.create(
                name=fake.name(),
                email=fake.email(),
                subject=fake.sentence(6),
                message=fake.text(500),
                created_at=fake.date_time_between(start_date='-3m', end_date='now', tzinfo=timezone.get_current_timezone()),
                is_read=choice([True, False, False]),  # Most unread
                referrer_page=choice(['/projects/', '/blog/', '/about/', '/']),
                user_agent=fake.user_agent(),
                ip_address=fake.ipv4(),
                response_sent=choice([True, False, False, False]),  # Few responses sent
                inquiry_category=choice(inquiry_types),
                priority=choice(priorities)
            )
            
        self.stdout.write('Created 15 contact form submissions')

    def create_systems(self):
        """Create project systems"""
        systems_data = [
            {
                'name': 'Portfolio Website',
                'description': 'Django-powered portfolio site with blog, projects showcase, and admin dashboard',
                'category': 'web_application',
                'status': 'active',
                'difficulty': 'intermediate',
                'github_url': 'https://github.com/yourhandle/portfolio-project'
            },
            {
                'name': 'Task Management API',
                'description': 'FastAPI-based task management system with user authentication and real-time updates',
                'category': 'api',
                'status': 'completed',
                'difficulty': 'advanced',
                'github_url': 'https://github.com/yourhandle/task-api'
            },
            {
                'name': 'Data Analysis Dashboard',
                'description': 'Interactive dashboard for analyzing sales data with Pandas and Plotly',
                'category': 'data_analysis',
                'status': 'in_development',
                'difficulty': 'intermediate',
                'github_url': 'https://github.com/yourhandle/data-dashboard'
            },
            {
                'name': 'Weather Monitor Bot',
                'description': 'Telegram bot that provides weather updates and alerts using OpenWeatherMap API',
                'category': 'automation',
                'status': 'completed',
                'difficulty': 'beginner',
                'github_url': 'https://github.com/yourhandle/weather-bot'
            },
            {
                'name': 'E-commerce Platform',
                'description': 'Full-featured e-commerce platform with payment processing and inventory management',
                'category': 'web_application',
                'status': 'planning',
                'difficulty': 'expert',
                'github_url': 'https://github.com/yourhandle/ecommerce-platform'
            }
        ]
        
        systems = []
        for i, sys_data in enumerate(systems_data):
            system, created = SystemModule.objects.get_or_create(
                name=sys_data['name'],
                defaults={
                    'slug': slugify(sys_data['name']),
                    'description': sys_data['description'],
                    'detailed_description': fake.text(1000),
                    'system_category': sys_data['category'],
                    'status': sys_data['status'],
                    'difficulty_level': sys_data['difficulty'],
                    'github_url': sys_data['github_url'],
                    'live_url': fake.url() if randint(0, 1) else '',
                    'is_featured': choice([True, False]),
                    'display_order': i + 1,
                    'completion_percentage': randint(60, 100) if sys_data['status'] != 'planning' else randint(10, 30),
                    'created_at': fake.date_time_between(start_date='-2y', end_date='now', tzinfo=timezone.get_current_timezone()),
                    'last_updated': fake.date_time_between(start_date='-1m', end_date='now', tzinfo=timezone.get_current_timezone()),
                }
            )
            systems.append(system)
            
            # Add technologies to system
            system_techs = sample(self.technologies, randint(3, 6))
            system.technologies.set(system_techs)
            
            if created:
                self.stdout.write(f'Created system: {system.name}')
                
        self.stdout.write(f'Created {len(systems)} systems')
        return systems

    def create_system_features(self):
        """Create features for systems"""
        feature_templates = [
            'User Authentication & Authorization',
            'Responsive Web Design',
            'REST API Integration',
            'Real-time Notifications',
            'Data Visualization',
            'File Upload & Management',
            'Search & Filtering',
            'Admin Dashboard',
            'Email Integration',
            'Caching & Performance Optimization',
            'Database Optimization',
            'Unit & Integration Testing',
            'CI/CD Pipeline',
            'Docker Containerization',
            'Cloud Deployment'
        ]
        
        features_created = 0
        for system in self.systems:
            num_features = randint(3, 8)
            selected_features = sample(feature_templates, min(num_features, len(feature_templates)))
            
            for i, feature_name in enumerate(selected_features):
                feature, created = SystemFeature.objects.get_or_create(
                    system=system,
                    name=feature_name,
                    defaults={
                        'description': fake.text(200),
                        'implementation_status': choice(['completed', 'in_progress', 'planned']),
                        'complexity_rating': randint(1, 5),
                        'display_order': i + 1,
                        'is_key_feature': choice([True, False]),
                    }
                )
                if created:
                    features_created += 1
                    
        self.stdout.write(f'Created {features_created} system features')

    def create_system_images(self):
        """Create placeholder system images"""
        image_types = ['screenshot', 'diagram', 'mockup', 'logo']
        
        images_created = 0
        for system in self.systems:
            num_images = randint(1, 4)
            
            for i in range(num_images):
                image, created = SystemImage.objects.get_or_create(
                    system=system,
                    image='placeholder.jpg',  # You'd replace with actual images
                    defaults={
                        'caption': fake.sentence(8),
                        'alt_text': f'{system.name} {choice(image_types)}',
                        'image_type': choice(image_types),
                        'display_order': i + 1,
                        'is_featured': i == 0,  # First image is featured
                    }
                )
                if created:
                    images_created += 1
                    
        self.stdout.write(f'Created {images_created} system images')

    def create_github_repos(self):
        """Create GitHub repository records"""
        repos_created = 0
        
        for system in self.systems:
            if system.github_url:
                repo_name = system.github_url.split('/')[-1]
                repo, created = GitHubRepository.objects.get_or_create(
                    system=system,
                    name=repo_name,
                    defaults={
                        'github_url': system.github_url,
                        'description': system.description,
                        'stars': randint(0, 50),
                        'forks': randint(0, 10),
                        'watchers': randint(0, 20),
                        'issues_open': randint(0, 5),
                        'language': choice(['Python', 'JavaScript', 'TypeScript']),
                        'size': randint(100, 10000),
                        'created_at': fake.date_time_between(start_date='-2y', end_date='now', tzinfo=timezone.get_current_timezone()),
                        'updated_at': fake.date_time_between(start_date='-1m', end_date='now', tzinfo=timezone.get_current_timezone()),
                        'is_private': False,
                        'is_active': True,
                    }
                )
                if created:
                    repos_created += 1
                    
        self.stdout.write(f'Created {repos_created} GitHub repositories')

    def create_system_commit_data(self):
        """Create commit tracking data"""
        commit_data_created = 0
        
        for system in self.systems:
            if hasattr(system, 'github_repository'):
                # Create weekly commit data for the last 12 weeks
                for week in range(12):
                    week_date = timezone.now().date() - timedelta(weeks=week)
                    
                    commit_data, created = SystemCommitData.objects.get_or_create(
                        system=system,
                        date=week_date,
                        defaults={
                            'commits': randint(0, 20),
                            'additions': randint(0, 500),
                            'deletions': randint(0, 200),
                            'files_changed': randint(0, 15),
                        }
                    )
                    if created:
                        commit_data_created += 1
                        
        self.stdout.write(f'Created {commit_data_created} commit data entries')

    def create_learning_milestones(self):
        """Create learning milestones"""
        milestone_templates = [
            'Completed Django Tutorial',
            'Built First REST API',
            'Deployed to Production',
            'Implemented User Authentication',
            'Added Real-time Features',
            'Optimized Database Queries',
            'Set up CI/CD Pipeline',
            'Containerized with Docker',
            'Added Unit Tests',
            'Implemented Caching'
        ]
        
        milestones_created = 0
        for system in self.systems:
            num_milestones = randint(2, 5)
            selected_milestones = sample(milestone_templates, min(num_milestones, len(milestone_templates)))
            
            for milestone_name in selected_milestones:
                milestone, created = LearningMilestone.objects.get_or_create(
                    system=system,
                    title=milestone_name,
                    defaults={
                        'description': fake.text(200),
                        'achieved_date': fake.date_between(start_date='-1y', end_date='today'),
                        'difficulty_rating': randint(1, 5),
                        'time_invested_hours': randint(5, 40),
                        'skills_gained': fake.sentence(10),
                        'is_major_milestone': choice([True, False]),
                    }
                )
                if created:
                    milestones_created += 1
                    
        self.stdout.write(f'Created {milestones_created} learning milestones')

    def create_architecture_components(self):
        """Create system architecture components"""
        component_types = [
            ('frontend', 'Frontend Application'),
            ('backend', 'Backend API'),
            ('database', 'Database'),
            ('cache', 'Cache Layer'),
            ('queue', 'Message Queue'),
            ('storage', 'File Storage'),
            ('auth', 'Authentication Service'),
            ('api_gateway', 'API Gateway'),
        ]
        
        components_created = 0
        for system in self.systems:
            num_components = randint(3, 6)
            selected_types = sample(component_types, min(num_components, len(component_types)))
            
            for comp_type, comp_name in selected_types:
                component, created = ArchitectureComponent.objects.get_or_create(
                    system=system,
                    name=f'{system.name} {comp_name}',
                    defaults={
                        'component_type': comp_type,
                        'description': fake.text(150),
                        'x_position': randint(50, 950),
                        'y_position': randint(50, 550),
                        'width': randint(120, 200),
                        'height': randint(80, 120),
                        'color': choice(['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']),
                        'icon': f'fas fa-{comp_type}',
                    }
                )
                if created:
                    components_created += 1
                    
        self.stdout.write(f'Created {components_created} architecture components')

    def create_architecture_connections(self):
        """Create connections between architecture components"""
        connections_created = 0
        
        for system in self.systems:
            components = list(ArchitectureComponent.objects.filter(system=system))
            if len(components) < 2:
                continue
                
            # Create 2-4 connections per system
            num_connections = randint(2, min(4, len(components) - 1))
            
            for _ in range(num_connections):
                from_comp = choice(components)
                to_comp = choice([c for c in components if c != from_comp])
                
                connection, created = ArchitectureConnection.objects.get_or_create(
                    from_component=from_comp,
                    to_component=to_comp,
                    defaults={
                        'connection_type': choice(['data_flow', 'api_call', 'dependency']),
                        'label': fake.word().capitalize(),
                        'line_color': choice(['#00ffff', '#ff00ff', '#ffff00']),
                        'line_width': randint(1, 3),
                        'is_bidirectional': choice([True, False]),
                    }
                )
                if created:
                    connections_created += 1
                    
        self.stdout.write(f'Created {connections_created} architecture connections')

    def create_blog_categories(self):
        """Create blog categories"""
        categories_data = [
            {'name': 'Machine Learning', 'code': 'ML', 'color': '#e91e63', 'icon': 'fas fa-robot'},
            {'name': 'Web Development', 'code': 'WD', 'color': '#2196f3', 'icon': 'fas fa-code'},
            {'name': 'Data Science', 'code': 'DS', 'color': '#ff9800', 'icon': 'fas fa-chart-line'},
            {'name': 'DevOps', 'code': 'DO', 'color': '#4caf50', 'icon': 'fas fa-server'},
            {'name': 'Tutorials', 'code': 'TU', 'color': '#9c27b0', 'icon': 'fas fa-book'},
            {'name': 'Project Updates', 'code': 'PU', 'color': '#00bcd4', 'icon': 'fas fa-project-diagram'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'code': cat_data['code'],
                    'description': fake.text(200),
                    'color': cat_data['color'],
                    'icon': cat_data['icon'],
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')
                
        self.stdout.write(f'Created {len(categories)} blog categories')
        return categories

    def create_blog_tags(self):
        """Create blog tags"""
        tag_names = [
            'python', 'django', 'javascript', 'react', 'api', 'database',
            'postgresql', 'docker', 'aws', 'machine-learning', 'data-analysis',
            'web-scraping', 'automation', 'testing', 'deployment', 'performance',
            'security', 'tutorial', 'beginner', 'advanced'
        ]
        
        tags = []
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={'slug': slugify(tag_name)}
            )
            tags.append(tag)
            if created:
                self.stdout.write(f'Created tag: {tag.name}')
                
        self.stdout.write(f'Created {len(tags)} blog tags')
        return tags

    def create_blog_posts(self):
        """Create blog posts"""
        posts_data = [
            {
                'title': 'Building a Django Portfolio Site: Complete Guide',
                'content': fake.text(2000),
                'status': 'published',
                'featured': True,
            },
            {
                'title': 'FastAPI vs Django: Performance Comparison',
                'content': fake.text(1500),
                'status': 'published',
                'featured': True,
            },
            {
                'title': 'Data Analysis with Pandas: Tips and Tricks',
                'content': fake.text(1800),
                'status': 'published',
                'featured': False,
            },
            {
                'title': 'Docker Deployment Strategies for Python Apps',
                'content': fake.text(1600),
                'status': 'published',
                'featured': False,
            },
            {
                'title': 'Machine Learning Model Deployment Guide',
                'content': fake.text(1200),
                'status': 'draft',
                'featured': False,
            },
            {
                'title': 'PostgreSQL Optimization Techniques',
                'content': fake.text(1400),
                'status': 'published',
                'featured': False,
            },
            {
                'title': 'Building Real-time Applications with WebSockets',
                'content': fake.text(1700),
                'status': 'published',
                'featured': False,
            },
            {
                'title': 'AWS Lambda for Python Developers',
                'content': fake.text(1300),
                'status': 'draft',
                'featured': False,
            }
        ]
        
        posts = []
        author = self.users[0]  # Use first user as author
        
        for post_data in posts_data:
            post, created = Post.objects.get_or_create(
                title=post_data['title'],
                defaults={
                    'slug': slugify(post_data['title']),
                    'content': post_data['content'],
                    'excerpt': fake.text(200),
                    'status': post_data['status'],
                    'featured': post_data['featured'],
                    'author': author,
                    'category': choice(self.categories),
                    'reading_time': randint(5, 15),
                    'show_toc': choice([True, False]),
                    'featured_code': fake.text(300) if choice([True, False]) else '',
                    'featured_code_format': choice(['python', 'javascript', 'sql']) if choice([True, False]) else '',
                    'created_at': fake.date_time_between(start_date='-6m', end_date='now', tzinfo=timezone.get_current_timezone()),
                    'updated_at': fake.date_time_between(start_date='-1m', end_date='now', tzinfo=timezone.get_current_timezone()),
                }
            )
            
            # Add random tags to post
            post_tags = sample(self.tags, randint(2, 5))
            post.tags.set(post_tags)
            
            posts.append(post)
            if created:
                self.stdout.write(f'Created post: {post.title}')
                
        self.stdout.write(f'Created {len(posts)} blog posts')
        return posts

    def create_comments(self):
        """Create blog post comments"""
        comments_created = 0
        
        for post in self.posts:
            if post.status == 'published':
                num_comments = randint(0, 8)
                
                for _ in range(num_comments):
                    comment = Comment.objects.create(
                        post=post,
                        name=fake.name(),
                        email=fake.email(),
                        content=fake.text(300),
                        created_at=fake.date_time_between(
                            start_date=post.created_at.date(),
                            end_date='now',
                            tzinfo=timezone.get_current_timezone()
                        ),
                        approved=choice([True, True, True, False])  # Most approved
                    )
                    comments_created += 1
                    
        self.stdout.write(f'Created {comments_created} blog comments')

    def create_post_views(self):
        """Create post view tracking"""
        views_created = 0
        
        for post in self.posts:
            if post.status == 'published':
                num_views = randint(10, 500)
                
                for _ in range(num_views):
                    view, created = PostView.objects.get_or_create(
                        post=post,
                        ip_address=fake.ipv4(),
                        defaults={
                            'viewed_on': fake.date_time_between(
                                start_date=post.created_at.date(),
                                end_date='now',
                                tzinfo=timezone.get_current_timezone()
                            )
                        }
                    )
                    if created:
                        views_created += 1
                        
        self.stdout.write(f'Created {views_created} post views')

    def create_blog_series(self):
        """Create blog post series"""
        series_data = [
            {
                'title': 'Django Mastery Series',
                'description': 'Complete guide to building production-ready Django applications',
                'difficulty': 'intermediate',
            },
            {
                'title': 'Data Science with Python',
                'description': 'From pandas basics to machine learning deployment',
                'difficulty': 'beginner',
            },
            {
                'title': 'Cloud Deployment Guide',
                'description': 'Deploy Python applications to AWS, GCP, and Azure',
                'difficulty': 'advanced',
            }
        ]
        
        series = []
        for series_info in series_data:
            blog_series, created = Series.objects.get_or_create(
                title=series_info['title'],
                defaults={
                    'slug': slugify(series_info['title']),
                    'description': series_info['description'],
                    'difficulty_level': series_info['difficulty'],
                    'is_complete': choice([True, False]),
                    'is_featured': choice([True, False]),
                }
            )
            series.append(blog_series)
            if created:
                self.stdout.write(f'Created series: {blog_series.title}')
                
        self.stdout.write(f'Created {len(series)} blog series')
        return series

    def create_series_posts(self):
        """Assign posts to series"""
        assignments_created = 0
        
        for blog_series in self.series:
            # Assign 2-4 posts per series
            num_posts = randint(2, 4)
            available_posts = [p for p in self.posts if p.status == 'published']
            selected_posts = sample(available_posts, min(num_posts, len(available_posts)))
            
            for order, post in enumerate(selected_posts, 1):
                series_post, created = SeriesPost.objects.get_or_create(
                    series=blog_series,
                    post=post,
                    defaults={'order': order}
                )
                if created:
                    assignments_created += 1
                    
        self.stdout.write(f'Created {assignments_created} series post assignments')

    def create_system_log_entries(self):
        """Create connections between blog posts and systems"""
        connections_created = 0
        
        for post in self.posts:
            if post.status == 'published':
                # Connect 0-2 systems per post
                num_connections = randint(0, 2)
                if num_connections > 0:
                    connected_systems = sample(self.systems, min(num_connections, len(self.systems)))
                    
                    for system in connected_systems:
                        log_entry, created = SystemLogEntry.objects.get_or_create(
                            post=post,
                            system=system,
                            defaults={
                                'connection_type': choice(['development', 'documentation', 'analysis', 'tutorial']),
                                'priority': randint(1, 4),
                                'log_entry_id': f'SYS-{system.id:03d}-LOG-{post.id:03d}',
                                'notes': fake.sentence(12),
                                'created_at': fake.date_time_between(
                                    start_date=post.created_at.date(),
                                    end_date='now',
                                    tzinfo=timezone.get_current_timezone()
                                ),
                            }
                        )
                        if created:
                            connections_created += 1
                            
        self.stdout.write(f'Created {connections_created} system log entries')

    def create_portfolio_analytics(self):
        """Create portfolio analytics data"""
        # Create daily analytics for the last 30 days
        analytics_created = 0
        
        for days_back in range(30):
            date = timezone.now().date() - timedelta(days=days_back)
            
            analytics, created = PortfolioAnalytics.objects.get_or_create(
                date=date,
                defaults={
                    'page_views': randint(20, 200),
                    'unique_visitors': randint(15, 150),
                    'session_duration_avg': randint(60, 300),  # seconds
                    'bounce_rate': round(random.uniform(0.3, 0.8), 2),
                    'blog_views': randint(5, 80),
                    'project_views': randint(3, 50),
                    'contact_form_submissions': randint(0, 5),
                    'top_referrer': choice(['google', 'github', 'linkedin', 'direct', 'twitter']),
                    'top_page': choice(['/blog/', '/projects/', '/', '/about/']),
                    'mobile_percentage': round(random.uniform(0.4, 0.7), 2),
                }
            )
            if created:
                analytics_created += 1
                
        self.stdout.write(f'Created {analytics_created} analytics entries')

    def stdout_summary(self):
        """Print a summary of created data"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('DATA POPULATION SUMMARY')
        self.stdout.write('='*50)
        
        # Count objects
        counts = {
            'Users': User.objects.count(),
            'Core Pages': CorePage.objects.count(),
            'Skills': Skill.objects.count(),
            'Technologies': Technology.objects.count(),
            'Education': Education.objects.count(),
            'Experience': Experience.objects.count(),
            'Social Links': SocialLink.objects.count(),
            'Contacts': Contact.objects.count(),
            'Systems': SystemModule.objects.count(),
            'System Features': SystemFeature.objects.count(),
            'GitHub Repos': GitHubRepository.objects.count(),
            'Blog Categories': Category.objects.count(),
            'Blog Tags': Tag.objects.count(),
            'Blog Posts': Post.objects.count(),
            'Comments': Comment.objects.count(),
            'Blog Series': Series.objects.count(),
            'Analytics Entries': PortfolioAnalytics.objects.count(),
        }
        
        for item, count in counts.items():
            self.stdout.write(f'{item}: {count}')
            
        self.stdout.write('\n🎉 Database successfully populated with sample data!')
        self.stdout.write('You can now test your portfolio site features.')
        self.stdout.write('\nTip: Use --clear flag to reset data before repopulating.')