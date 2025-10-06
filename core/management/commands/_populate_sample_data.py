"""
Django Management Command to Populate Sample Data - Updated for Skill-Technology Restructure
File: core/management/commands/populate_sample_data.py

Creates comprehensive sample data across all apps with correct skill-technology relationships:
- Core: Pages, Skills (conceptual), Education, Experience, Contacts, Social Links, SkillTechnologyRelations
- Projects: Technologies (concrete), Systems, Features, GitHub repos, Architecture, SystemSkillGains with technologies_used
- Blog: Categories, Tags, Posts, Comments, Series, System Connections  
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
    SystemSkillGain, SystemCommitData, GitHubRepository,
    GitHubCommitWeek, LearningMilestone, ArchitectureComponent,
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
        self.create_skill_technology_relations()  # New relationship model
        self.educations = self.create_education()
        self.create_education_skill_development()
        self.create_experience()
        self.create_social_links()
        self.create_contacts()
        
        # Projects app data
        self.systems = self.create_systems()
        self.create_system_features()
        self.create_system_images()
        self.create_system_skill_gains()  # Updated with technologies_used
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
        GitHubCommitWeek.objects.all().delete()
        SystemCommitData.objects.all().delete()
        LearningMilestone.objects.all().delete()
        ArchitectureComponent.objects.all().delete()
        
        # Clear main models
        Post.objects.all().delete()
        Series.objects.all().delete()
        SystemModule.objects.all().delete()
        GitHubRepository.objects.all().delete()
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
        """Create test users."""
        users = []
        for i in range(count):
            username = f'testuser{i+1}' if count > 1 else 'admin'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                    'is_staff': True,
                    'is_superuser': True,
                }
            )
            if created:
                user.set_password('admin123')
                user.save()
                self.stdout.write(f'Created user: {user.username}')
            users.append(user)
        return users

    def create_core_pages(self):
        """Create core pages."""
        pages_data = [
            {'title': 'Home', 'slug': 'home', 'content': fake.text(500)},
            {'title': 'About', 'slug': 'about', 'content': fake.text(1000)},
            {'title': 'Contact', 'slug': 'contact', 'content': fake.text(300)},
        ]
        
        for page_data in pages_data:
            page, created = CorePage.objects.get_or_create(
                slug=page_data['slug'],
                defaults={
                    'title': page_data['title'],
                    'content': page_data['content'],
                }
            )
            if created:
                self.stdout.write(f'Created page: {page.title}')

    def create_skills(self):
        """Create conceptual skills (not technologies)"""
        # Updated to focus on conceptual skills, not concrete technologies
        skills_data = [
            # Technical Concepts
            {'name': 'Web Development', 'category': 'technical_concept', 'proficiency': 5, 'featured': True},
            {'name': 'API Design', 'category': 'technical_concept', 'proficiency': 4, 'featured': True},
            {'name': 'Database Design', 'category': 'technical_concept', 'proficiency': 4, 'featured': True},
            {'name': 'Machine Learning', 'category': 'technical_concept', 'proficiency': 3, 'featured': True},
            {'name': 'Data Analysis', 'category': 'technical_concept', 'proficiency': 4, 'featured': False},
            {'name': 'System Architecture', 'category': 'technical_concept', 'proficiency': 3, 'featured': False},
            {'name': 'DevOps Practices', 'category': 'technical_concept', 'proficiency': 3, 'featured': False},
            {'name': 'Testing Strategy', 'category': 'technical_concept', 'proficiency': 4, 'featured': False},
            
            # Methodologies
            {'name': 'Agile Development', 'category': 'methodology', 'proficiency': 4, 'featured': False},
            {'name': 'Code Review', 'category': 'methodology', 'proficiency': 4, 'featured': False},
            {'name': 'Documentation', 'category': 'methodology', 'proficiency': 4, 'featured': False},
            {'name': 'Version Control', 'category': 'methodology', 'proficiency': 5, 'featured': False},
            
            # Soft Skills
            {'name': 'Problem Solving', 'category': 'soft_skill', 'proficiency': 5, 'featured': True},
            {'name': 'Technical Communication', 'category': 'soft_skill', 'proficiency': 4, 'featured': False},
            {'name': 'Team Collaboration', 'category': 'soft_skill', 'proficiency': 4, 'featured': False},
            {'name': 'Mentoring', 'category': 'soft_skill', 'proficiency': 3, 'featured': False},
            
            # Domain Knowledge
            {'name': 'Environmental Science', 'category': 'domain_knowledge', 'proficiency': 5, 'featured': True},
            {'name': 'Health & Safety', 'category': 'domain_knowledge', 'proficiency': 4, 'featured': False},
            {'name': 'Regulatory Compliance', 'category': 'domain_knowledge', 'proficiency': 4, 'featured': False},
        ]
        
        skills = []
        for skill_data in skills_data:
            skill, created = Skill.objects.get_or_create(
                name=skill_data['name'],
                defaults={
                    'slug': slugify(skill_data['name']),
                    'category': skill_data['category'],
                    'proficiency': skill_data['proficiency'],
                    'is_featured': skill_data.get('featured', False),
                    'is_certified': randint(0, 1) == 1,
                    'is_currently_learning': randint(0, 3) == 1,  # 25% chance
                    'description': fake.text(200),
                    'years_experience': randint(1, 8),
                    'color': choice(['#26c6da', '#b39ddb', '#ff8a80', '#fff59d', '#a5d6a7']),
                    'icon': choice(['fa-brain', 'fa-cogs', 'fa-lightbulb', 'fa-puzzle-piece']),
                    'last_used': fake.date_between(start_date='-1y', end_date='today'),
                }
            )
            skills.append(skill)
            if created:
                self.stdout.write(f'Created skill: {skill.name}')
                
        self.stdout.write(f'Created {len(skills)} skills')
        return skills

    def create_technologies(self):
        """Create concrete technologies from projects app"""
        tech_data = [
            # Programming Languages
            {'name': 'Python', 'category': 'language', 'color': '#3776ab', 'icon': 'fab fa-python'},
            {'name': 'JavaScript', 'category': 'language', 'color': '#f7df1e', 'icon': 'fab fa-js-square'},
            {'name': 'HTML/CSS', 'category': 'language', 'color': '#e34f26', 'icon': 'fab fa-html5'},
            {'name': 'SQL', 'category': 'language', 'color': '#4479a1', 'icon': 'fas fa-database'},
            {'name': 'Rust', 'category': 'language', 'color': '#000000', 'icon': 'fab fa-rust'},
            
            # Frameworks & Libraries
            {'name': 'Django', 'category': 'framework', 'color': '#092e20', 'icon': 'fas fa-server'},
            {'name': 'FastAPI', 'category': 'framework', 'color': '#009688', 'icon': 'fas fa-code'},
            {'name': 'React', 'category': 'framework', 'color': '#61dafb', 'icon': 'fab fa-react'},
            {'name': 'Vue.js', 'category': 'framework', 'color': '#4fc08d', 'icon': 'fab fa-vuejs'},
            {'name': 'Pandas', 'category': 'framework', 'color': '#150458', 'icon': 'fas fa-chart-bar'},
            {'name': 'NumPy', 'category': 'framework', 'color': '#013243', 'icon': 'fas fa-microscope'},
            {'name': 'Scikit-learn', 'category': 'framework', 'color': '#f7931e', 'icon': 'fas fa-flask'},
            {'name': 'TensorFlow', 'category': 'ai', 'color': '#ff6f00', 'icon': 'fas fa-brain'},
            
            # Databases
            {'name': 'PostgreSQL', 'category': 'database', 'color': '#336791', 'icon': 'fas fa-database'},
            {'name': 'Redis', 'category': 'database', 'color': '#dc382d', 'icon': 'fas fa-database'},
            {'name': 'SQLite', 'category': 'database', 'color': '#003b57', 'icon': 'fas fa-database'},
            
            # Tools & Platforms
            {'name': 'Docker', 'category': 'tool', 'color': '#2496ed', 'icon': 'fab fa-docker'},
            {'name': 'Git', 'category': 'tool', 'color': '#f05032', 'icon': 'fab fa-git-alt'},
            {'name': 'Linux', 'category': 'os', 'color': '#fcc624', 'icon': 'fab fa-linux'},
            {'name': 'VS Code', 'category': 'tool', 'color': '#007acc', 'icon': 'fas fa-code'},
            {'name': 'Nginx', 'category': 'tool', 'color': '#009639', 'icon': 'fas fa-cogs'},
            {'name': 'Celery', 'category': 'tool', 'color': '#37b24d', 'icon': 'fas fa-check'},
            
            # Cloud Services
            {'name': 'AWS', 'category': 'cloud', 'color': '#ff9900', 'icon': 'fab fa-aws'},
            {'name': 'Render', 'category': 'cloud', 'color': '#46e3b7', 'icon': 'fas fa-diagram-project'},
            {'name': 'Heroku', 'category': 'cloud', 'color': '#430098', 'icon': 'fas fa-cloud'},
        ]
        
        technologies = []
        for tech in tech_data:
            technology, created = Technology.objects.get_or_create(
                name=tech['name'],
                defaults={
                    'slug': slugify(tech['name']),
                    'category': tech['category'],
                    'color': tech['color'],
                    'description': fake.text(150),
                    'icon': f"fab fa-{tech['name'].lower().replace('.', '').replace('/', '')}",
                }
            )
            technologies.append(technology)
            if created:
                self.stdout.write(f'Created technology: {technology.name}')
                
        self.stdout.write(f'Created {len(technologies)} technologies')
        return technologies

    def create_skill_technology_relations(self):
        """Create relationships between conceptual skills and concrete technologies"""
        relations_created = 0
        
        # Define logical skill-technology mappings
        skill_tech_mappings = {
            'Web Development': ['Python', 'Django', 'JavaScript', 'HTML/CSS', 'PostgreSQL'],
            'API Design': ['Python', 'Django', 'FastAPI', 'PostgreSQL'],
            'Database Design': ['PostgreSQL', 'Redis', 'SQLite', 'SQL'],
            'Machine Learning': ['Python', 'TensorFlow', 'Scikit-learn', 'Pandas', 'NumPy'],
            'Data Analysis': ['Python', 'Pandas', 'NumPy', 'PostgreSQL'],
            'System Architecture': ['Docker', 'Nginx', 'PostgreSQL', 'Redis'],
            'DevOps Practices': ['Docker', 'Linux', 'AWS', 'Git', 'Nginx'],
            'Testing Strategy': ['Python', 'Django'],
            'Version Control': ['Git'],
        }
        
        for skill in self.skills:
            tech_names = skill_tech_mappings.get(skill.name, [])
            
            for tech_name in tech_names:
                try:
                    technology = next(t for t in self.technologies if t.name == tech_name)
                    
                    # Determine relationship strength and type based on skill and technology
                    strength = randint(2, 4)  # Common to Primary implementation
                    relationship_types = ['implementation', 'supporting', 'primary_implementation']
                    rel_type = choice(relationship_types)
                    
                    relation, created = SkillTechnologyRelation.objects.get_or_create(
                        skill=skill,
                        technology=technology,
                        defaults={
                            'strength': strength,
                            'relationship_type': rel_type,
                            'notes': f"Used {technology.name} for {skill.name.lower()} projects",
                            'first_used_together': fake.date_between(start_date='-3y', end_date='-1y'),
                            'last_used_together': fake.date_between(start_date='-6m', end_date='today'),
                        }
                    )
                    
                    if created:
                        relations_created += 1
                        
                except StopIteration:
                    continue  # Technology not found, skip
            
            # Also create some random relationships for variety
            if randint(1, 3) == 1:  # 33% chance
                random_tech = choice(self.technologies)
                if not SkillTechnologyRelation.objects.filter(skill=skill, technology=random_tech).exists():
                    SkillTechnologyRelation.objects.create(
                        skill=skill,
                        technology=random_tech,
                        strength=randint(1, 2),  # Occasionally to commonly used
                        relationship_type='supporting',
                        notes=f"Occasionally used {random_tech.name} in {skill.name.lower()} context",
                    )
                    relations_created += 1
                    
        self.stdout.write(f'Created {relations_created} skill-technology relations')

    def create_education(self):
        """Create education entries with all required fields"""
        education_data = [
            {
                'institution': 'Stanford Online',
                'degree': 'CS106A Programming Abstractions',
                'field_of_study': 'Computer Science',
                'start_date': date(2022, 1, 15),
                'end_date': date(2022, 4, 30),
                'learning_type': 'online_course',
                'hours': 120,
            },
            {
                'institution': 'University of Michigan (Coursera)',
                'degree': 'Python for Everybody Specialization',
                'field_of_study': 'Python Programming',
                'start_date': date(2021, 9, 1),
                'end_date': date(2022, 1, 10),
                'learning_type': 'online_course',
                'hours': 200,
            },
            {
                'institution': 'FreeCodeCamp',
                'degree': 'Full Stack Web Development Certificate',
                'field_of_study': 'Web Development',
                'start_date': date(2022, 5, 1),
                'end_date': date(2022, 11, 15),
                'learning_type': 'certification',
                'hours': 300,
            },
            {
                'institution': 'AWS',
                'degree': 'AWS Certified Developer Associate',
                'field_of_study': 'Cloud Computing',
                'start_date': date(2023, 1, 1),
                'end_date': date(2023, 3, 15),
                'learning_type': 'certification',
                'hours': 80,
            },
            {
                'institution': 'State University',
                'degree': 'Bachelor of Science in Environmental Science',
                'field_of_study': 'Environmental Science',
                'start_date': date(2015, 8, 1),
                'end_date': date(2019, 5, 15),
                'learning_type': 'formal_degree',
                'hours': 2400,
            }
        ]
        
        educations = []
        for edu_data in education_data:
            education, created = Education.objects.get_or_create(
                institution=edu_data['institution'],
                degree=edu_data['degree'],
                defaults={
                    'slug': slugify(f"{edu_data['degree']}-{edu_data['institution']}"),
                    'field_of_study': edu_data['field_of_study'],
                    'start_date': edu_data['start_date'],
                    'end_date': edu_data['end_date'],
                    'description': fake.text(300),
                    'learning_type': edu_data['learning_type'],
                    'is_completed': True,
                    'grade': choice(['A', 'A-', 'B+', 'Pass', 'Distinction']),
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
        """Create skill development through education with correct field names"""
        developments_created = 0
        
        # Define which skills were developed in which education programs
        education_skill_mappings = {
            'CS106A Programming Abstractions': ['Problem Solving', 'Technical Communication'],
            'Python for Everybody Specialization': ['Web Development', 'API Design', 'Database Design'],
            'Full Stack Web Development Certificate': ['Web Development', 'System Architecture', 'Problem Solving'],
            'AWS Certified Developer Associate': ['DevOps Practices', 'System Architecture'],
            'Bachelor of Science in Environmental Science': ['Environmental Science', 'Health & Safety', 'Regulatory Compliance', 'Data Analysis'],
        }
        
        for education in self.educations:
            skill_names = education_skill_mappings.get(education.degree, [])
            
            # Get matching skills
            matching_skills = [s for s in self.skills if s.name in skill_names]
            
            # Also add some random skills
            if len(matching_skills) < 3:
                random_skills = sample([s for s in self.skills if s not in matching_skills], 
                                     min(2, len(self.skills) - len(matching_skills)))
                matching_skills.extend(random_skills)
            
            for skill in matching_skills[:6]:  # Max 6 skills per education
                development, created = EducationSkillDevelopment.objects.get_or_create(
                    education=education,
                    skill=skill,
                    defaults={
                        'proficiency_before': randint(0, 2),
                        'proficiency_after': randint(3, 5),
                        'learning_focus': choice(['foundation', 'advanced', 'practical', 'theoretical']),
                        'importance_level': randint(1, 5),
                        'learning_notes': f"Developed {skill.name.lower()} skills through {education.degree}"
                    }
                )
                if created:
                    developments_created += 1
                    
        self.stdout.write(f'Created {developments_created} education skill developments')

    def create_experience(self):
        """Create work experience entries with required fields"""
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
                'start_date': date(2021, 3, 1),
                'end_date': date(2022, 5, 31),
                'current': False,
                'technologies': 'Python, Django, React, PostgreSQL'
            },
            {
                'company': 'Environmental Consulting Group',
                'position': 'Environmental Health Specialist',
                'location': 'Portland, OR',
                'start_date': date(2019, 6, 1),
                'end_date': date(2021, 2, 28),
                'current': False,
                'technologies': 'Excel, GIS, Database Management'
            }
        ]
        
        for exp_data in experience_data:
            experience, created = Experience.objects.get_or_create(
                company=exp_data['company'],
                position=exp_data['position'],
                defaults={
                    'slug': slugify(f"{exp_data['position']}-{exp_data['company']}"),
                    'location': exp_data['location'],
                    'description': fake.text(400),
                    'start_date': exp_data['start_date'],
                    'end_date': exp_data['end_date'],
                    'is_current': exp_data['current'],
                    'technologies': exp_data['technologies'],
                }
            )
            if created:
                self.stdout.write(f'Created experience: {experience.position} at {experience.company}')

    def create_social_links(self):
        """Create social media links"""
        social_data = [
            {'platform': 'GitHub', 'url': 'https://github.com/username', 'icon': 'fab fa-github', 'color': '#546e7a', 'category': 'professional'},
            {'platform': 'LinkedIn', 'url': 'https://linkedin.com/in/username', 'icon': 'fab fa-linkedin', 'color': '#0077b5', 'category': 'professional'},
            {'platform': 'Twitter', 'url': 'https://twitter.com/username', 'icon': 'fab fa-twitter', 'color': '#1da1f2', 'category': 'chat'},
            {'platform': 'Stack Overflow', 'url': 'https://stackoverflow.com/users/username', 'icon': 'fab fa-stack-overflow', 'color': '#FFBD2E', 'category': 'community'},
        ]
        
        for social in social_data:
            link, created = SocialLink.objects.get_or_create(
                name=social['platform'],
                defaults={
                    'url': social['url'],
                    'icon': social['icon'],
                    'category': social['category'],
                    'color': social['color']
                }
            )
            if created:
                self.stdout.write(f'Created social link: {link.name}')

    def create_contacts(self):
        """Create contact information"""
        contact_data = [
            {'type': 'email', 'value': 'developer@example.com', 'icon': 'fas fa-envelope'},
            {'type': 'phone', 'value': '+1 (555) 123-4567', 'icon': 'fas fa-phone'},
            {'type': 'location', 'value': 'San Francisco, CA', 'icon': 'fas fa-map-marker-alt'},
        ]
        
        for contact_info in contact_data:
            contact, created = Contact.objects.get_or_create(
                contact_type=contact_info['type'],
                defaults={
                    'value': contact_info['value'],
                    'icon': contact_info['icon'],
                }
            )
            if created:
                self.stdout.write(f'Created contact: {contact.contact_type}')

    def create_systems(self):
        """Create system modules with required fields"""
        system_data = [
            {
                'title': 'Portfolio Website',
                'description': 'Django-based portfolio website with HUD theme',
                'status': 'deployed',
                'priority': 4,
                'completion_percent': 85,
            },
            {
                'title': 'Task Management API',
                'description': 'REST API for task management with authentication',
                'status': 'deployed',
                'priority': 3,
                'completion_percent': 90,
            },
            {
                'title': 'Data Analysis Dashboard',
                'description': 'Interactive dashboard for environmental data visualization',
                'status': 'in_development',
                'priority': 3,
                'completion_percent': 60,
            },
            {
                'title': 'Machine Learning Classifier',
                'description': 'ML model for predicting environmental compliance',
                'status': 'in_development',
                'priority': 2,
                'completion_percent': 25,
            },
        ]
        
        systems = []
        for sys_data in system_data:
            system, created = SystemModule.objects.get_or_create(
                title=sys_data['title'],
                defaults={
                    'slug': slugify(sys_data['title']),
                    'subtitle': sys_data['description'],
                    'status': sys_data['status'],
                    'priority': sys_data['priority'],
                    'completion_percent': sys_data['completion_percent'],
                    'description': fake.text(800),
                    'complexity': randint(1, 5),
                    'featured': randint(0, 1) == 1,
                    'github_url': fake.url(),
                    'live_url': fake.url() if randint(0, 1) else '',
                    'learning_stage': choice(['tutorial', 'guided', 'independent', 'refactoring', 'contributing', 'teaching']),
                }
            )
            systems.append(system)
            if created:
                self.stdout.write(f'Created system: {system.title}')
        
        return systems

    def create_system_features(self):
        """Create system features"""
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
            # Create 2-5 features per system
            num_features = randint(2, 5)
            selected_features = sample(feature_templates, min(num_features, len(feature_templates)))
            
            for i, feature_name in enumerate(selected_features):
                feature, created = SystemFeature.objects.get_or_create(
                    system=system,
                    title=fake.catch_phrase(),
                    defaults={
                        'description': fake.text(100),
                        'implementation_status': choice(['completed', 'in_progress', 'planned']),
                        'feature_type': choice(['core', 'advanced', 'integration', 'performance', 'security', 'ui']),
                        'icon': choice(['fas fa-key', 'fas fa-cogs', 'fas fa-check', 'fas fa-user']),
                    }
                )
                if created:
                    features_created += 1
                    
        self.stdout.write(f'Created {features_created} system features')

    def create_system_images(self):
        """Create placeholder system images"""
        images_created = 0
        
        for system in self.systems:
            # Create 1-3 images per system
            num_images = randint(1, 3)
            
            for i in range(num_images):
                image, created = SystemImage.objects.get_or_create(
                    system=system,
                    title=f"{system.title} Screenshot {i+1}",
                    defaults={
                        'image': f'systems/placeholder_{i+1}.jpg',  # Placeholder path
                        'description': fake.text(100),
                        'is_featured': i == 0,  # First image is featured
                        'display_order': i + 1,
                    }
                )
                if created:
                    images_created += 1
                    
        self.stdout.write(f'Created {images_created} system images')

    def create_system_skill_gains(self):
        """Create system skill gains with the new technologies_used field"""
        gains_created = 0
        
        for system in self.systems:
            # Each system should have 3-6 skill gains
            selected_skills = sample(self.skills, randint(3, 6))
            
            for skill in selected_skills:
                gain, created = SystemSkillGain.objects.get_or_create(
                    system=system,
                    skill=skill,
                    defaults={
                        'proficiency_gained': randint(2, 5),
                        'how_learned': f"Applied {skill.name.lower()} concepts while building {system.title}",
                        'skill_level_before': randint(1, 3),
                        'skill_level_after': randint(3, 5),
                    }
                )
                
                if created:
                    gains_created += 1
                    
                    # NEW: Add technologies used for this skill gain
                    # Find technologies related to this skill
                    skill_relations = SkillTechnologyRelation.objects.filter(skill=skill)
                    if skill_relations.exists():
                        # Add 1-3 technologies that were used
                        related_techs = [rel.technology for rel in skill_relations[:3]]
                        gain.technologies_used.set(related_techs)
                    else:
                        # Add 1-2 random technologies
                        random_techs = sample(self.technologies, randint(1, 2))
                        gain.technologies_used.set(random_techs)
                        
        self.stdout.write(f'Created {gains_created} system skill gains with technology relationships')

    def create_github_repos(self):
        """Create GitHub repository data"""
        repos_created = 0
        
        for system in self.systems:
            repo, created = GitHubRepository.objects.get_or_create(
                name=slugify(system.title),
                defaults={
                    'full_name': f'username/{slugify(system.title)}',
                    'description': system.description,
                    'url': f'https://github.com/username/{slugify(system.title)}',
                    'language': choice(['Python', 'JavaScript', 'TypeScript']),
                    'stars': randint(0, 50),
                    'forks': randint(0, 10),
                    'open_issues': randint(0, 5),
                    'size': randint(100, 10000),
                    'created_at': fake.date_time_between(start_date='-2y', end_date='now', tzinfo=timezone.utc),
                    'updated_at': fake.date_time_between(start_date='-1m', end_date='now', tzinfo=timezone.utc),
                    'pushed_at': fake.date_time_between(start_date='-1w', end_date='now', tzinfo=timezone.utc),
                }
            )
            if created:
                repos_created += 1
                
        self.stdout.write(f'Created {repos_created} GitHub repositories')

    def create_system_commit_data(self):
        """Create commit data for systems"""
        commits_created = 0
        
        for system in self.systems:
            commit, created = SystemCommitData.objects.get_or_create(
                system=system,
                defaults={
                    'total_commits': randint(20, 200),
                    'commits_last_month': randint(5, 50),
                    'last_commit_date': fake.date_between(start_date='-1m', end_date='today'),
                    'commit_frequency': choice(['daily', 'weekly', 'monthly']),
                    'last_updated': timezone.now(),
                }
            )
            if created:
                commits_created += 1
                
        self.stdout.write(f'Created {commits_created} system commit data entries')

    def create_learning_milestones(self):
        """Create learning milestone entries"""
        milestone_data = [
            {'title': 'First Python Program', 'description': 'Wrote my first "Hello World" in Python', 'date': date(2021, 8, 1)},
            {'title': 'First Web Application', 'description': 'Built first Django web app', 'date': date(2022, 2, 15)},
            {'title': 'Database Integration', 'description': 'Successfully integrated PostgreSQL', 'date': date(2022, 4, 10)},
            {'title': 'API Development', 'description': 'Created first REST API with authentication', 'date': date(2022, 7, 20)},
            {'title': 'Deployment Success', 'description': 'First successful production deployment', 'date': date(2022, 10, 5)},
        ]
        
        milestones_created = 0
        for milestone in milestone_data:
            obj, created = LearningMilestone.objects.get_or_create(
                title=milestone['title'],
                defaults={
                    'description': milestone['description'],
                    'date_achieved': milestone['date'],
                    'milestone_type': choice(['first_time', 'breakthrough', 'completion', 'deployment', 'debugging', 'teaching']),
                    'difficulty_level': randint(1, 5),
                    'confidence_boost': randint(1, 5),
                }
            )
            if created:
                milestones_created += 1
                
        self.stdout.write(f'Created {milestones_created} learning milestones')

    def create_architecture_components(self):
        """Create architecture components"""
        components_created = 0
        
        component_data = [
            {'name': 'Frontend', 'type': 'frontend', 'description': 'User interface layer'},
            {'name': 'API Gateway', 'type': 'api', 'description': 'API routing and authentication'},
            {'name': 'Database', 'type': 'database', 'description': 'Data persistence layer'},
            {'name': 'Cache Layer', 'type': 'database', 'description': 'Redis caching system'},
            {'name': 'Background Jobs', 'type': 'processing', 'description': 'Celery task processing'},
        ]
        
        for system in self.systems:
            for comp_data in component_data[:randint(3, 5)]:  # 3-5 components per system
                component, created = ArchitectureComponent.objects.get_or_create(
                    system=system,
                    name=comp_data['name'],
                    defaults={
                        'component_type': comp_data['type'],
                        'description': comp_data['description'],
                        'position_x': randint(100, 800),
                        'position_y': randint(100, 600),
                        'color': choice(['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']),
                    }
                )
                if created:
                    components_created += 1
                    
        self.stdout.write(f'Created {components_created} architecture components')

    def create_architecture_connections(self):
        """Create connections between architecture components"""
        connections_created = 0
        
        # Get all components grouped by system
        for system in self.systems:
            components = ArchitectureComponent.objects.filter(system=system)
            
            # Create some connections between components
            for i, component in enumerate(components):
                # Connect to 1-2 other components
                other_components = components.exclude(id=component.id)
                if other_components.exists():
                    targets = sample(list(other_components), min(2, len(other_components)))
                    
                    for target in targets:
                        connection, created = ArchitectureConnection.objects.get_or_create(
                            from_component=component,
                            to_component=target,
                            defaults={
                                'connection_type': choice(['data_flow', 'api_call', 'dependency', 'file_transfer']),
                                'label': f'{component.name} → {target.name}',
                                'line_color': choice(['#26c6da', '#b39ddb', '#ff8a80']),
                                'line_width': randint(1, 3),
                                'is_bidirectional': randint(0, 1) == 1,
                            }
                        )
                        if created:
                            connections_created += 1
                            
        self.stdout.write(f'Created {connections_created} architecture connections')

    def create_blog_categories(self):
        """Create blog categories with required fields"""
        category_data = [
            {'name': 'Development', 'code': 'DEV', 'color': '#26c6da', 'icon': 'fas fa-code'},
            {'name': 'Machine Learning', 'code': 'ML', 'color': '#b39ddb', 'icon': 'fas fa-robot'},
            {'name': 'DevOps', 'code': 'OPS', 'color': '#ff8a80', 'icon': 'fas fa-server'},
            {'name': 'Learning', 'code': 'LRN', 'color': '#fff59d', 'icon': 'fas fa-graduation-cap'},
            {'name': 'Projects', 'code': 'PRJ', 'color': '#a5d6a7', 'icon': 'fas fa-project-diagram'},
        ]
        
        categories = []
        for cat_data in category_data:
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
                
        return categories

    def create_blog_tags(self):
        """Create blog tags"""
        tag_names = [
            'Python', 'Django', 'JavaScript', 'API', 'Database', 'Machine Learning',
            'Tutorial', 'Best Practices', 'Performance', 'Security', 'Testing',
            'Deployment', 'AWS', 'Docker', 'PostgreSQL'
        ]
        
        tags = []
        for name in tag_names:
            tag, created = Tag.objects.get_or_create(
                name=name,
                defaults={'slug': slugify(name)}
            )
            tags.append(tag)
            if created:
                self.stdout.write(f'Created tag: {tag.name}')
                
        return tags

    def create_blog_posts(self):
        """Create blog posts with all required fields"""
        posts = []
        author = self.users[0]  # Use first user as author
        
        for i in range(10):  # Create 10 sample posts
            post, created = Post.objects.get_or_create(
                title=fake.sentence(nb_words=6),
                defaults={
                    'slug': slugify(fake.sentence(nb_words=6)),
                    'content': fake.text(2000),
                    'excerpt': fake.text(200),
                    'author': author,
                    'category': choice(self.categories),
                    'status': choice(['published', 'draft']),
                    'featured': randint(0, 1) == 1,
                    'featured_code': fake.text(200) if randint(0, 1) else '',
                    'featured_code_format': choice(['python', 'javascript', 'html']),
                    'reading_time': randint(3, 15),
                    'show_toc': randint(0, 1) == 1,
                    'published_date': fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.utc) if choice(['published', 'draft']) == 'published' else None,
                }
            )
            
            if created:
                # Add random tags
                post.tags.set(sample(self.tags, randint(1, 4)))
                
                # Add random system connections
                if randint(0, 1):
                    post.related_systems.set(sample(self.systems, randint(1, 2)))
                
                posts.append(post)
                self.stdout.write(f'Created post: {post.title}')
                
        return posts

    def create_comments(self):
        """Create blog post comments"""
        comments_created = 0
        
        for post in self.posts:
            # Each post gets 0-5 comments
            num_comments = randint(0, 5)
            
            for i in range(num_comments):
                comment, created = Comment.objects.get_or_create(
                    post=post,
                    name=fake.name(),
                    defaults={
                        'email': fake.email(),
                        'content': fake.text(300),
                        'approved': randint(0, 1) == 1,
                    }
                )
                if created:
                    comments_created += 1
                    
        self.stdout.write(f'Created {comments_created} comments')

    def create_post_views(self):
        """Create post view tracking"""
        views_created = 0
        
        for post in self.posts:
            # Each post gets 5-50 unique views
            num_views = randint(5, 50)
            
            for i in range(num_views):
                view, created = PostView.objects.get_or_create(
                    post=post,
                    ip_address=fake.ipv4(),
                    defaults={
                        'viewed_on': fake.date_time_between(start_date='-6m', end_date='now', tzinfo=timezone.utc)
                    }
                )
                if created:
                    views_created += 1
                    
        self.stdout.write(f'Created {views_created} post views')

    def create_blog_series(self):
        """Create blog series"""
        series_data = [
            {'title': 'Django for Beginners', 'description': 'Learn Django from scratch'},
            {'title': 'API Development Guide', 'description': 'Building robust APIs'},
            {'title': 'Machine Learning Journey', 'description': 'My ML learning path'},
        ]
        
        series = []
        for series_info in series_data:
            s, created = Series.objects.get_or_create(
                title=series_info['title'],
                defaults={
                    'slug': slugify(series_info['title']),
                    'description': series_info['description'],
                    'difficulty_level': choice(['beginner', 'intermediate', 'advanced']),
                    'is_complete': randint(0, 1) == 1,
                    'is_featured': randint(0, 1) == 1,
                }
            )
            series.append(s)
            if created:
                self.stdout.write(f'Created series: {s.title}')
                
        return series

    def create_series_posts(self):
        """Create series-post relationships"""
        relationships_created = 0
        
        for series in self.series:
            # Each series gets 2-4 posts
            series_posts = sample(self.posts, randint(2, 4))
            
            for i, post in enumerate(series_posts):
                relationship, created = SeriesPost.objects.get_or_create(
                    series=series,
                    post=post,
                    defaults={'order': i + 1}
                )
                if created:
                    relationships_created += 1
                    
        self.stdout.write(f'Created {relationships_created} series-post relationships')

    def create_system_log_entries(self):
        """Create connections between posts and systems"""
        entries_created = 0
        
        for post in self.posts:
            if post.related_systems.exists():
                for system in post.related_systems.all():
                    entry, created = SystemLogEntry.objects.get_or_create(
                        post=post,
                        system=system,
                        defaults={
                            'connection_type': choice(['development', 'documentation', 'analysis']),
                            'priority': randint(1, 4),
                            'log_entry_id': f"SYS-{system.id:03d}-LOG-{post.id:03d}",
                        }
                    )
                    if created:
                        entries_created += 1
                        
        self.stdout.write(f'Created {entries_created} system log entries')

    def create_portfolio_analytics(self):
        """Create portfolio analytics data"""
        analytics, created = PortfolioAnalytics.objects.get_or_create(
            date=date.today(),
            defaults={
                'page_views': randint(500, 2000),
                'unique_visitors': randint(100, 500),
                'bounce_rate': round(random.uniform(0.2, 0.8), 2),
                'avg_session_duration': randint(120, 600),
                'top_pages': ['/', '/projects/', '/blog/', '/about/'],
                'referral_sources': ['google.com', 'github.com', 'linkedin.com'],
            }
        )
        if created:
            self.stdout.write('Created portfolio analytics data')