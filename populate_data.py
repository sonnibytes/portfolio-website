#!/usr/bin/env python
"""
Django Portfolio Data Population Script
Populates all models with comprehensive sample data for testing
Run with: python manage.py shell < populate_data.py
"""

import os
import sys
import django
from datetime import datetime, timedelta, date
from decimal import Decimal
import random

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_project.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone

# Import all models
from core.models import (
    CorePage, Skill, Education, EducationSkillDevelopment, Experience, 
    Contact, SocialLink, PortfolioAnalytics, SkillTechnologyRelation
)
from blog.models import (
    Category, Tag, Post, Comment, PostView, Series, SeriesPost, SystemLogEntry
)
from projects.models import (
    SystemType, Technology, SystemModule, SystemFeature, SystemChallenge,
    SystemSkillGain, SystemMetric, SystemDependency, ArchitectureComponent,
    ArchitectureConnection
)

def clear_all_data():
    """Clear existing data (optional - uncomment if needed)"""
    print("🗑️  Clearing existing data...")
    
    # Clear in reverse dependency order
    SystemLogEntry.objects.all().delete()
    SeriesPost.objects.all().delete()
    ArchitectureConnection.objects.all().delete()
    ArchitectureComponent.objects.all().delete()
    SystemDependency.objects.all().delete()
    SystemMetric.objects.all().delete()
    SystemSkillGain.objects.all().delete()
    SystemChallenge.objects.all().delete()
    SystemFeature.objects.all().delete()
    SystemModule.objects.all().delete()
    
    PostView.objects.all().delete()
    Comment.objects.all().delete()
    Post.objects.all().delete()
    Series.objects.all().delete()
    
    SkillTechnologyRelation.objects.all().delete()
    EducationSkillDevelopment.objects.all().delete()
    
    # Clear main models
    Technology.objects.all().delete()
    SystemType.objects.all().delete()
    Tag.objects.all().delete()
    Category.objects.all().delete()
    
    Contact.objects.all().delete()
    SocialLink.objects.all().delete()
    PortfolioAnalytics.objects.all().delete()
    Experience.objects.all().delete()
    Education.objects.all().delete()
    Skill.objects.all().delete()
    CorePage.objects.all().delete()
    
    # Keep superuser if exists
    User.objects.filter(is_superuser=False).delete()
    
    print("✅ Data cleared successfully")

def create_users():
    """Create sample users"""
    print("👤 Creating users...")
    
    # Create or get superuser
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@portfolio.dev',
            'first_name': 'Portfolio',
            'last_name': 'Admin',
            'is_superuser': True,
            'is_staff': True,
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
    
    # Create test users for comments
    test_users = [
        ('jane_dev', 'jane@example.com', 'Jane', 'Developer'),
        ('mike_hiring', 'mike@techcorp.com', 'Mike', 'Johnson'),
        ('sarah_mentor', 'sarah@mentor.dev', 'Sarah', 'Wilson'),
    ]
    
    users = [admin_user]
    for username, email, first_name, last_name in test_users:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            }
        )
        if created:
            user.set_password('test123')
            user.save()
        users.append(user)
    
    print(f"✅ Created {len(users)} users")
    return users

def create_core_pages():
    """Create core pages"""
    print("📄 Creating core pages...")
    
    pages_data = [
        {
            'title': 'About Me',
            'slug': 'about',
            'content': '''# From Environmental Health to Code
            
My journey into software development started with a curiosity for automation and problem-solving. 
With a background in Environmental Health & Safety, I've developed strong analytical skills and 
attention to detail that translate perfectly to writing clean, maintainable code.

## Current Focus
- **Backend Development**: Django, Python, PostgreSQL
- **Frontend Skills**: HTML/CSS, JavaScript, learning React
- **Learning Path**: Building full-stack applications, API development

## What I Bring
- **Analytical Mindset**: Years of data analysis and regulatory compliance
- **Problem Solving**: Complex safety assessments and risk management
- **Communication**: Technical documentation and stakeholder presentations
- **Continuous Learning**: Always adapting to new regulations... now new technologies!

*Ready to bring this unique perspective to your development team.*''',
            'meta_description': 'Environmental Health professional transitioning to software development with strong analytical and problem-solving skills.',
            'is_published': True,
        },
        {
            'title': 'Contact',
            'slug': 'contact',
            'content': '''# Let's Connect

Interested in discussing opportunities or have questions about my projects? 
I'd love to hear from you!

## Professional Availability
Currently seeking **junior developer positions** and **collaborative projects** 
that allow me to apply my Python/Django skills while continuing to grow.

## Response Time
I typically respond within 24 hours. For urgent inquiries, 
feel free to connect via LinkedIn.''',
            'meta_description': 'Get in touch to discuss development opportunities, projects, or technical questions.',
            'is_published': True,
        },
        {
            'title': 'Portfolio',
            'slug': 'portfolio',
            'content': '''# Project Portfolio

Welcome to my development journey! Each project represents hands-on learning 
and practical application of new technologies.

## Project Categories
- **Web Applications**: Full-stack Django projects
- **Data Analysis**: Python scripts and visualizations  
- **Learning Projects**: Coding challenges and tutorials
- **System Integrations**: APIs and automation tools

*Every project includes detailed documentation of challenges, 
solutions, and lessons learned.*''',
            'meta_description': 'Explore my software development projects showcasing Python, Django, and full-stack development skills.',
            'is_published': True,
        }
    ]
    
    pages = []
    for page_data in pages_data:
        page, created = CorePage.objects.get_or_create(
            slug=page_data['slug'],
            defaults=page_data
        )
        pages.append(page)
    
    print(f"✅ Created {len(pages)} core pages")
    return pages

def create_skills():
    """Create skills data"""
    print("🛠️  Creating skills...")
    
    skills_data = [
        # Programming Languages
        {'name': 'Python', 'category': 'programming', 'proficiency': 85, 'color': '#3776ab', 'icon': 'fab fa-python', 'is_featured': True},
        {'name': 'JavaScript', 'category': 'programming', 'proficiency': 70, 'color': '#f7df1e', 'icon': 'fab fa-js-square', 'is_featured': True},
        {'name': 'HTML/CSS', 'category': 'programming', 'proficiency': 80, 'color': '#e34c26', 'icon': 'fab fa-html5', 'is_featured': True},
        {'name': 'SQL', 'category': 'programming', 'proficiency': 75, 'color': '#336791', 'icon': 'fas fa-database'},
        
        # Frameworks & Libraries
        {'name': 'Django', 'category': 'framework', 'proficiency': 80, 'color': '#092e20', 'icon': 'fas fa-server', 'is_featured': True},
        {'name': 'React', 'category': 'framework', 'proficiency': 45, 'color': '#61dafb', 'icon': 'fab fa-react'},
        {'name': 'Bootstrap', 'category': 'framework', 'proficiency': 75, 'color': '#7952b3', 'icon': 'fab fa-bootstrap'},
        {'name': 'jQuery', 'category': 'framework', 'proficiency': 65, 'color': '#0769ad', 'icon': 'fas fa-code'},
        
        # Databases & Tools
        {'name': 'PostgreSQL', 'category': 'database', 'proficiency': 70, 'color': '#336791', 'icon': 'fas fa-database'},
        {'name': 'SQLite', 'category': 'database', 'proficiency': 75, 'color': '#003b57', 'icon': 'fas fa-database'},
        {'name': 'Git/GitHub', 'category': 'tool', 'proficiency': 80, 'color': '#f05032', 'icon': 'fab fa-git-alt', 'is_featured': True},
        {'name': 'VS Code', 'category': 'tool', 'proficiency': 85, 'color': '#007acc', 'icon': 'fas fa-code'},
        {'name': 'Command Line', 'category': 'tool', 'proficiency': 75, 'color': '#000000', 'icon': 'fas fa-terminal'},
        
        # Data & Analysis
        {'name': 'Pandas', 'category': 'data', 'proficiency': 70, 'color': '#150458', 'icon': 'fas fa-chart-line'},
        {'name': 'Matplotlib', 'category': 'data', 'proficiency': 65, 'color': '#11557c', 'icon': 'fas fa-chart-bar'},
        {'name': 'Data Analysis', 'category': 'data', 'proficiency': 80, 'color': '#ff6b6b', 'icon': 'fas fa-analytics'},
        
        # Professional Skills
        {'name': 'Problem Solving', 'category': 'soft', 'proficiency': 90, 'color': '#4ecdc4', 'icon': 'fas fa-lightbulb'},
        {'name': 'Technical Writing', 'category': 'soft', 'proficiency': 85, 'color': '#45b7d1', 'icon': 'fas fa-pen'},
        {'name': 'Project Management', 'category': 'soft', 'proficiency': 80, 'color': '#96ceb4', 'icon': 'fas fa-tasks'},
    ]
    
    skills = []
    for skill_data in skills_data:
        skill, created = Skill.objects.get_or_create(
            name=skill_data['name'],
            defaults={
                'category': skill_data['category'],
                'proficiency': skill_data['proficiency'],
                'color': skill_data['color'],
                'icon': skill_data['icon'],
                'is_featured': skill_data.get('is_featured', False),
                'description': f"Proficient in {skill_data['name']} with practical project experience.",
                'years_experience': random.randint(1, 3),
            }
        )
        skills.append(skill)
    
    print(f"✅ Created {len(skills)} skills")
    return skills

def create_technologies():
    """Create technologies data"""
    print("🔧 Creating technologies...")
    
    tech_data = [
        # Languages
        {'name': 'Python', 'category': 'language', 'color': '#3776ab', 'icon': 'fab fa-python', 'is_featured': True},
        {'name': 'JavaScript', 'category': 'language', 'color': '#f7df1e', 'icon': 'fab fa-js-square', 'is_featured': True},
        {'name': 'HTML5', 'category': 'language', 'color': '#e34c26', 'icon': 'fab fa-html5'},
        {'name': 'CSS3', 'category': 'language', 'color': '#1572b6', 'icon': 'fab fa-css3-alt'},
        {'name': 'SQL', 'category': 'language', 'color': '#336791', 'icon': 'fas fa-database'},
        
        # Frameworks
        {'name': 'Django', 'category': 'framework', 'color': '#092e20', 'icon': 'fas fa-server', 'is_featured': True},
        {'name': 'React', 'category': 'framework', 'color': '#61dafb', 'icon': 'fab fa-react'},
        {'name': 'Bootstrap', 'category': 'framework', 'color': '#7952b3', 'icon': 'fab fa-bootstrap'},
        {'name': 'Tailwind CSS', 'category': 'framework', 'color': '#06b6d4', 'icon': 'fas fa-wind'},
        
        # Databases
        {'name': 'PostgreSQL', 'category': 'database', 'color': '#336791', 'icon': 'fas fa-database', 'is_featured': True},
        {'name': 'SQLite', 'category': 'database', 'color': '#003b57', 'icon': 'fas fa-database'},
        {'name': 'Redis', 'category': 'database', 'color': '#dc382d', 'icon': 'fas fa-memory'},
        
        # Tools
        {'name': 'Git', 'category': 'tool', 'color': '#f05032', 'icon': 'fab fa-git-alt', 'is_featured': True},
        {'name': 'Docker', 'category': 'tool', 'color': '#2496ed', 'icon': 'fab fa-docker'},
        {'name': 'Heroku', 'category': 'tool', 'color': '#430098', 'icon': 'fas fa-cloud'},
        {'name': 'VS Code', 'category': 'tool', 'color': '#007acc', 'icon': 'fas fa-code'},
        
        # Libraries
        {'name': 'Pandas', 'category': 'library', 'color': '#150458', 'icon': 'fas fa-chart-line'},
        {'name': 'Requests', 'category': 'library', 'color': '#FF6B6B', 'icon': 'fas fa-exchange-alt'},
        {'name': 'Matplotlib', 'category': 'library', 'color': '#11557c', 'icon': 'fas fa-chart-bar'},
        {'name': 'BeautifulSoup', 'category': 'library', 'color': '#4ECDC4', 'icon': 'fas fa-soup'},
    ]
    
    technologies = []
    for tech in tech_data:
        technology, created = Technology.objects.get_or_create(
            name=tech['name'],
            defaults={
                'category': tech['category'],
                'color': tech['color'],
                'icon': tech['icon'],
                'is_featured': tech.get('is_featured', False),
                'description': f"{tech['name']} - {tech['category'].title()} technology used in various projects.",
                'website_url': f"https://{tech['name'].lower().replace(' ', '')}.org" if tech['category'] in ['language', 'framework'] else "",
            }
        )
        technologies.append(technology)
    
    print(f"✅ Created {len(technologies)} technologies")
    return technologies

def create_education(skills):
    """Create education data"""
    print("🎓 Creating education...")
    
    education_data = [
        {
            'institution': 'Self-Directed Learning',
            'degree': 'Python & Django Development',
            'field_of_study': 'Computer Science',
            'start_date': date(2023, 1, 15),
            'end_date': None,
            'is_current': True,
            'gpa': 0.0,
            'description': '''Comprehensive self-study program focusing on Python development and Django framework:

• **Python Fundamentals**: Data structures, OOP, file handling, error management
• **Web Development**: Django MVT architecture, templates, forms, user authentication  
• **Database Design**: SQL, ORM relationships, migrations, data modeling
• **Frontend Integration**: HTML/CSS, JavaScript, responsive design principles
• **Version Control**: Git workflows, GitHub collaboration, code documentation
• **Deployment**: Heroku deployment, environment configuration, production basics

**Learning Resources**: Real Python, Django Documentation, MDN Web Docs, FreeCodeCamp
**Practice Projects**: Personal portfolio, blog applications, data analysis tools''',
            'achievements': [
                'Built 5+ complete Django applications',
                'Mastered MVT architecture and Django ORM',
                'Developed responsive frontend skills',
                'Established daily coding practice routine'
            ]
        },
        {
            'institution': 'University of Environmental Studies',
            'degree': 'Bachelor of Science',
            'field_of_study': 'Environmental Health & Safety',
            'start_date': date(2016, 9, 1),
            'end_date': date(2020, 5, 15),
            'is_current': False,
            'gpa': 3.7,
            'description': '''Comprehensive environmental health program with strong emphasis on data analysis and regulatory compliance:

• **Data Analysis**: Statistical analysis of environmental samples and health metrics
• **Risk Assessment**: Quantitative risk modeling and safety protocol development  
• **Regulatory Compliance**: Understanding complex regulatory frameworks and documentation
• **Research Methods**: Scientific methodology, data collection, and technical reporting
• **Problem Solving**: Root cause analysis and systematic troubleshooting approaches
• **Communication**: Technical writing, presentations, and stakeholder engagement

**Key Transferable Skills**: Attention to detail, analytical thinking, process documentation, continuous learning mindset - all directly applicable to software development quality practices.''',
            'achievements': [
                'Graduated Magna Cum Laude (3.7 GPA)',
                'Senior Capstone: Data Analysis Project',
                'Research Assistant for 2 semesters',
                'Environmental Health Society President'
            ]
        }
    ]
    
    education_records = []
    for edu_data in education_data:
        achievements_str = '\n'.join([f"• {achievement}" for achievement in edu_data.pop('achievements')])
        edu_data['achievements'] = achievements_str
        
        education, created = Education.objects.get_or_create(
            institution=edu_data['institution'],
            degree=edu_data['degree'],
            defaults=edu_data
        )
        education_records.append(education)
    
    # Create skill development relationships
    skill_developments = []
    
    # Self-Directed Learning skill development
    self_directed = education_records[0]
    programming_skills = [
        ('Python', 0, 4),
        ('JavaScript', 0, 3),
        ('HTML/CSS', 0, 4),
        ('Django', 0, 4),
        ('PostgreSQL', 0, 3),
        ('Git/GitHub', 0, 4),
        ('Problem Solving', 3, 5),
    ]
    
    for skill_name, before, after in programming_skills:
        skill = next((s for s in skills if s.name == skill_name), None)
        if skill:
            dev, created = EducationSkillDevelopment.objects.get_or_create(
                education=self_directed,
                skill=skill,
                defaults={
                    'proficiency_before': before,
                    'proficiency_after': after,
                    'learning_focus': 'practical',
                    'importance_level': 5 if skill_name in ['Python', 'Django'] else 4,
                    'learning_notes': f'Intensive hands-on learning of {skill_name} through projects and documentation.'
                }
            )
            skill_developments.append(dev)
    
    # University skill development  
    university = education_records[1]
    academic_skills = [
        ('Data Analysis', 1, 4),
        ('Technical Writing', 1, 4),
        ('Problem Solving', 2, 5),
        ('Project Management', 0, 3),
    ]
    
    for skill_name, before, after in academic_skills:
        skill = next((s for s in skills if s.name == skill_name), None)
        if skill:
            dev, created = EducationSkillDevelopment.objects.get_or_create(
                education=university,
                skill=skill,
                defaults={
                    'proficiency_before': before,
                    'proficiency_after': after,
                    'learning_focus': 'theoretical',
                    'importance_level': 4,
                    'learning_notes': f'Developed {skill_name} through academic coursework and research projects.'
                }
            )
            skill_developments.append(dev)
    
    print(f"✅ Created {len(education_records)} education records with {len(skill_developments)} skill developments")
    return education_records

def create_experience():
    """Create work experience"""
    print("💼 Creating work experience...")
    
    experiences_data = [
        {
            'company': 'Environmental Solutions Corp',
            'position': 'Environmental Health Specialist',
            'location': 'Portland, OR',
            'start_date': date(2021, 3, 1),
            'end_date': date(2023, 12, 31),
            'is_current': False,
            'technologies': 'Excel, SQL, Python (basic), GIS Software, Statistical Analysis',
            'description': '''**Data-Driven Environmental Health Professional** with strong analytical and problem-solving skills directly transferable to software development.

**Key Responsibilities:**
• **Data Analysis & Reporting**: Analyzed complex environmental datasets using SQL queries and Python scripts for statistical analysis and trend identification
• **Process Automation**: Developed Excel macros and Python scripts to automate repetitive data processing tasks, reducing processing time by 60%
• **Technical Documentation**: Created comprehensive technical reports, SOPs, and compliance documentation with attention to detail and clarity
• **Problem Solving**: Conducted root cause analysis for environmental incidents, developing systematic approaches to complex problems
• **Stakeholder Communication**: Presented technical findings to both technical and non-technical audiences, translating complex data into actionable insights

**Technical Skills Developed:**
• Advanced Excel and database management
• Basic Python scripting for data analysis
• SQL for database queries and reporting
• Process documentation and quality assurance
• Regulatory compliance and systematic thinking

**Why This Matters for Development**: The analytical mindset, attention to detail, and systematic problem-solving approach from environmental health translate directly to writing clean, maintainable code and debugging complex systems.'''
        },
        {
            'company': 'Freelance Development',
            'position': 'Junior Python Developer',
            'location': 'Remote',
            'start_date': date(2023, 6, 1),
            'end_date': None,
            'is_current': True,
            'technologies': 'Python, Django, PostgreSQL, HTML/CSS, JavaScript, Git, Heroku',
            'description': '''**Transitioning to Software Development** through hands-on project work and continuous learning.

**Current Projects & Learning:**
• **Portfolio Website**: Built this Django-based portfolio showcasing technical projects with responsive design and database integration
• **Task Management App**: Developed a full-stack Django application with user authentication, CRUD operations, and REST API endpoints
• **Data Analysis Tools**: Created Python scripts for data visualization and analysis, applying programming skills to familiar domain expertise
• **Open Source Contributions**: Contributing to beginner-friendly open source projects to build collaboration skills

**Technical Growth:**
• **Backend Development**: Django models, views, templates, forms, and admin interface
• **Frontend Skills**: Responsive HTML/CSS, JavaScript for interactive features
• **Database Design**: PostgreSQL modeling, migrations, and optimization
• **Version Control**: Git workflows, branching strategies, and collaborative development
• **Deployment**: Heroku deployment, environment configuration, and production debugging

**Professional Development:**
• Daily coding practice with consistent GitHub contributions
• Technical blog writing to document learning journey
• Networking with local developer community through meetups
• Continuous learning through online courses and documentation

*Ready to bring analytical thinking, attention to detail, and eagerness to learn to a development team.*'''
        }
    ]
    
    experiences = []
    for exp_data in experiences_data:
        exp, created = Experience.objects.get_or_create(
            company=exp_data['company'],
            position=exp_data['position'],
            defaults=exp_data
        )
        experiences.append(exp)
    
    print(f"✅ Created {len(experiences)} experience records")
    return experiences

def create_social_links():
    """Create social media links"""
    print("🔗 Creating social links...")
    
    social_data = [
        {'name': 'GitHub', 'url': 'https://github.com/yourusername', 'handle': '@yourusername', 
         'icon': 'fab fa-github', 'category': 'professional', 'color': '#333333', 'display_order': 1},
        {'name': 'LinkedIn', 'url': 'https://linkedin.com/in/yourprofile', 'handle': 'Your Name', 
         'icon': 'fab fa-linkedin', 'category': 'professional', 'color': '#0077b5', 'display_order': 2},
        {'name': 'Dev.to', 'url': 'https://dev.to/yourusername', 'handle': '@yourusername', 
         'icon': 'fab fa-dev', 'category': 'blog', 'color': '#0a0a0a', 'display_order': 3},
        {'name': 'Twitter', 'url': 'https://twitter.com/yourusername', 'handle': '@yourusername', 
         'icon': 'fab fa-twitter', 'category': 'community', 'color': '#1da1f2', 'display_order': 4},
        {'name': 'Stack Overflow', 'url': 'https://stackoverflow.com/users/yourid', 'handle': 'Your Profile', 
         'icon': 'fab fa-stack-overflow', 'category': 'community', 'color': '#f48024', 'display_order': 5},
    ]
    
    social_links = []
    for social in social_data:
        link, created = SocialLink.objects.get_or_create(
            name=social['name'],
            defaults=social
        )
        social_links.append(link)
    
    print(f"✅ Created {len(social_links)} social links")
    return social_links

def create_system_types():
    """Create system types"""
    print("🏗️  Creating system types...")
    
    types_data = [
        {'name': 'Web Application', 'code': 'WEB', 'color': '#26c6da', 'icon': 'fas fa-globe', 
         'description': 'Full-stack web applications built with Django'},
        {'name': 'Data Analysis', 'code': 'DATA', 'color': '#b39ddb', 'icon': 'fas fa-chart-line', 
         'description': 'Python scripts and tools for data analysis and visualization'},
        {'name': 'API Service', 'code': 'API', 'color': '#ff8a80', 'icon': 'fas fa-plug', 
         'description': 'REST APIs and web services'},
        {'name': 'Automation Tool', 'code': 'AUTO', 'color': '#fff59d', 'icon': 'fas fa-robot', 
         'description': 'Scripts and tools for process automation'},
        {'name': 'Learning Project', 'code': 'LEARN', 'color': '#a5d6a7', 'icon': 'fas fa-graduation-cap', 
         'description': 'Educational projects and coding challenges'},
    ]
    
    system_types = []
    for type_data in types_data:
        sys_type, created = SystemType.objects.get_or_create(
            name=type_data['name'],
            defaults=type_data
        )
        system_types.append(sys_type)
    
    print(f"✅ Created {len(system_types)} system types")
    return system_types

def create_categories_and_tags():
    """Create blog categories and tags"""
    print("🏷️  Creating categories and tags...")
    
    categories_data = [
        {'name': 'Development', 'code': 'DEV', 'color': '#26c6da', 'icon': 'fas fa-code', 
         'description': 'Software development insights and tutorials'},
        {'name': 'Learning', 'code': 'LRN', 'color': '#b39ddb', 'icon': 'fas fa-brain', 
         'description': 'Learning journey and skill development'},
        {'name': 'Projects', 'code': 'PRJ', 'color': '#ff8a80', 'icon': 'fas fa-rocket', 
         'description': 'Project showcases and development logs'},
        {'name': 'Tutorial', 'code': 'TUT', 'color': '#a5d6a7', 'icon': 'fas fa-chalkboard-teacher', 
         'description': 'Step-by-step guides and tutorials'},
        {'name': 'Analysis', 'code': 'ANA', 'color': '#fff59d', 'icon': 'fas fa-analytics', 
         'description': 'Technical analysis and problem-solving'},
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        categories.append(category)
    
    # Create tags
    tags_list = [
        'python', 'django', 'javascript', 'html-css', 'postgresql', 'git',
        'learning', 'tutorial', 'beginner', 'portfolio', 'deployment', 'debugging',
        'data-analysis', 'automation', 'api', 'frontend', 'backend', 'full-stack',
        'problem-solving', 'career-change', 'self-taught', 'documentation'
    ]
    
    tags = []
    for tag_name in tags_list:
        tag, created = Tag.objects.get_or_create(
            name=tag_name,
            defaults={'slug': slugify(tag_name)}
        )
        tags.append(tag)
    
    print(f"✅ Created {len(categories)} categories and {len(tags)} tags")
    return categories, tags

def create_systems(system_types, technologies, skills):
    """Create sample systems (projects)"""
    print("🚀 Creating systems...")
    
    systems_data = [
        {
            'title': 'AURA Portfolio System',
            'subtitle': 'Personal portfolio with HUD-inspired design',
            'system_type': 'Web Application',
            'status': 'published',
            'complexity': 4,
            'priority': 4,
            'technologies': ['Python', 'Django', 'PostgreSQL', 'HTML5', 'CSS3', 'JavaScript'],
            'skills': ['Python', 'Django', 'PostgreSQL', 'HTML/CSS', 'JavaScript'],
            'description': '''# AURA Portfolio System

A comprehensive portfolio website built with Django, featuring a futuristic HUD-inspired design. This system demonstrates full-stack development capabilities while showcasing my learning journey from Environmental Health to Software Development.

## Architecture Overview
The portfolio uses a modular Django architecture with three main applications:
- **Core**: Handles user profiles, skills, experience, and static content
- **Projects**: Manages the systems showcase with detailed technical information  
- **Blog**: Powers the "DataLogs" - technical blog entries documenting learning and development progress

## Key Technical Features
- **Responsive Design**: Mobile-first approach with progressive enhancement
- **Database Optimization**: Efficient queries with select_related and prefetch_related
- **Admin Interface**: Custom Django admin for easy content management
- **SEO Optimization**: Meta tags, sitemap, and structured data
- **Performance**: Caching strategies and optimized static file delivery''',
            'features': [
                'Responsive HUD-inspired design system',
                'Three-app Django architecture (Core, Projects, Blog)',
                'Custom admin interface with bulk operations',
                'Advanced database relationships and optimization',
                'SEO-friendly with meta tags and structured data',
                'Mobile-first responsive design',
                'Custom template tags and filters',
                'Automated deployment pipeline'
            ],
            'challenges': [
                'Complex model relationships between apps',
                'Custom admin interface design',
                'Performance optimization for large datasets',
                'Mobile responsiveness with complex animations'
            ],
            'metrics': {
                'Performance Score': 95,
                'SEO Score': 100,
                'Accessibility Score': 92,
                'Code Coverage': 85
            }
        },
        {
            'title': 'Task Management API',
            'subtitle': 'RESTful API for task and project management',
            'system_type': 'API Service',
            'status': 'deployed',
            'complexity': 3,
            'priority': 3,
            'technologies': ['Python', 'Django', 'PostgreSQL', 'Git'],
            'skills': ['Python', 'Django', 'PostgreSQL', 'Git/GitHub'],
            'description': '''# Task Management API

A RESTful API built with Django REST Framework for managing tasks, projects, and team collaboration. This project demonstrates backend development skills and API design principles.

## Core Functionality
- **User Authentication**: JWT-based authentication system
- **Task Management**: CRUD operations for tasks with priority levels
- **Project Organization**: Group tasks into projects with deadlines
- **Team Collaboration**: User assignments and permission levels
- **Filtering & Search**: Advanced query capabilities with pagination

## API Endpoints
The API provides comprehensive endpoints for:
- User registration and authentication
- Task creation, updating, and deletion
- Project management and team assignments
- Advanced filtering by status, priority, and due dates
- Real-time notifications for task updates''',
            'features': [
                'JWT authentication and authorization',
                'RESTful API design with proper HTTP methods',
                'Advanced filtering and search capabilities',
                'Pagination and sorting for large datasets',
                'Input validation and error handling',
                'API documentation with Swagger/OpenAPI',
                'Unit tests with 90%+ coverage',
                'Docker containerization'
            ],
            'challenges': [
                'Implementing complex filtering logic',
                'JWT token refresh mechanisms',
                'Optimizing database queries for performance',
                'Comprehensive API testing strategies'
            ],
            'metrics': {
                'API Response Time': 120,  # ms
                'Test Coverage': 92,
                'Documentation Score': 95,
                'Uptime': 99.8
            }
        },
        {
            'title': 'Environmental Data Analyzer',
            'subtitle': 'Python tool for analyzing environmental datasets',
            'system_type': 'Data Analysis',
            'status': 'published',
            'complexity': 3,
            'priority': 2,
            'technologies': ['Python', 'Pandas', 'Matplotlib', 'SQLite'],
            'skills': ['Python', 'Data Analysis', 'SQL'],
            'description': '''# Environmental Data Analyzer

A Python-based data analysis tool that bridges my Environmental Health background with programming skills. Processes and visualizes environmental monitoring data to identify trends and compliance issues.

## Data Processing Pipeline
1. **Data Ingestion**: Reads CSV, Excel, and database sources
2. **Data Cleaning**: Handles missing values and outliers
3. **Statistical Analysis**: Performs trend analysis and hypothesis testing
4. **Visualization**: Generates charts and reports
5. **Reporting**: Exports findings in multiple formats

## Business Impact
This tool automated previously manual processes, reducing analysis time from days to hours while improving accuracy and consistency of environmental reporting.''',
            'features': [
                'Multi-format data import (CSV, Excel, JSON)',
                'Automated data cleaning and validation',
                'Statistical analysis with scipy',
                'Interactive visualizations with Matplotlib',
                'PDF report generation',
                'Command-line interface',
                'Configuration-based analysis workflows',
                'Data export in multiple formats'
            ],
            'challenges': [
                'Handling inconsistent data formats',
                'Memory optimization for large datasets',
                'Creating user-friendly CLI interface',
                'Statistical significance testing'
            ],
            'metrics': {
                'Processing Speed': 50000,  # records/minute
                'Accuracy Improvement': 35,  # %
                'Time Saved': 80,  # %
                'User Satisfaction': 4.8  # out of 5
            }
        },
        {
            'title': 'Learning Progress Tracker',
            'subtitle': 'Personal dashboard for tracking coding progress',
            'system_type': 'Web Application',
            'status': 'in_development',
            'complexity': 2,
            'priority': 2,
            'technologies': ['Python', 'Django', 'JavaScript', 'Bootstrap'],
            'skills': ['Python', 'Django', 'JavaScript'],
            'description': '''# Learning Progress Tracker

A personal dashboard application for tracking daily coding activities, learning goals, and skill development progress. Built as a learning project to practice Django development while solving a real personal need.

## Features in Development
- **Daily Activity Logging**: Track coding hours, topics studied, and projects worked on
- **Goal Setting**: Set and monitor progress toward learning objectives
- **Skill Assessment**: Self-evaluation tools for tracking proficiency growth
- **Progress Visualization**: Charts and graphs showing learning trends
- **Resource Management**: Bookmark and categorize learning materials

This project serves as both a useful personal tool and a demonstration of iterative development practices.''',
            'features': [
                'Daily activity logging with time tracking',
                'Goal setting and progress monitoring',
                'Skill proficiency tracking',
                'Progress visualization with charts',
                'Resource bookmarking system',
                'Mobile-responsive design',
                'Data export capabilities',
                'Achievement system for motivation'
            ],
            'challenges': [
                'Designing intuitive user interface',
                'Creating meaningful progress metrics',
                'Implementing data visualization',
                'Balancing features with simplicity'
            ],
            'metrics': {
                'Development Progress': 70,  # %
                'Features Completed': 60,  # %
                'Test Coverage': 75,  # %
                'User Stories': 15  # completed
            }
        },
        {
            'title': 'Web Scraping Automation',
            'subtitle': 'Automated data collection and processing system',
            'system_type': 'Automation Tool',
            'status': 'deployed',
            'complexity': 3,
            'priority': 2,
            'technologies': ['Python', 'BeautifulSoup', 'Requests', 'SQLite'],
            'skills': ['Python', 'Problem Solving'],
            'description': '''# Web Scraping Automation

An automated web scraping system that collects and processes data from multiple sources. Demonstrates understanding of web technologies, data processing, and automation principles.

## Technical Implementation
- **Ethical Scraping**: Respects robots.txt and implements rate limiting
- **Data Processing**: Cleans and structures collected data
- **Storage**: Efficiently stores data in SQLite database
- **Scheduling**: Automated runs with cron jobs
- **Error Handling**: Robust exception handling and logging
- **Monitoring**: Tracks success rates and performance metrics

## Learning Outcomes
This project provided hands-on experience with HTTP protocols, HTML parsing, data structures, and automation concepts essential for web development.''',
            'features': [
                'Multi-site data collection with rate limiting',
                'Robust error handling and retry logic',
                'Data cleaning and validation pipelines',
                'Automated scheduling with cron jobs',
                'Comprehensive logging and monitoring',
                'CSV and JSON data export options',
                'Configuration-driven scraping rules',
                'Performance optimization for large datasets'
            ],
            'challenges': [
                'Handling dynamic content and JavaScript',
                'Implementing respectful rate limiting',
                'Managing connection timeouts and retries',
                'Data quality validation and cleaning'
            ],
            'metrics': {
                'Success Rate': 97.5,  # %
                'Data Points': 50000,  # collected
                'Processing Speed': 1000,  # records/hour
                'Uptime': 99.2  # %
            }
        }
    ]
    
    systems = []
    for sys_data in systems_data:
        # Find related models
        system_type = next((st for st in system_types if st.name == sys_data['system_type']), None)
        
        # Create system
        system_fields = {
            'title': sys_data['title'],
            'subtitle': sys_data['subtitle'],
            'system_type': system_type,
            'status': sys_data['status'],
            'complexity': sys_data['complexity'],
            'priority': sys_data['priority'],
            'description': sys_data['description'],
            'github_url': f"https://github.com/yourusername/{slugify(sys_data['title'])}",
            'demo_url': f"https://{slugify(sys_data['title'])}.herokuapp.com" if sys_data['status'] in ['deployed', 'published'] else "",
            'is_featured': sys_data.get('priority', 1) >= 3,
            'created_at': timezone.now() - timedelta(days=random.randint(30, 365)),
            'updated_at': timezone.now() - timedelta(days=random.randint(1, 30)),
        }
        
        system, created = SystemModule.objects.get_or_create(
            title=sys_data['title'],
            defaults=system_fields
        )
        
        if created:
            # Add technologies
            for tech_name in sys_data.get('technologies', []):
                tech = next((t for t in technologies if t.name == tech_name), None)
                if tech:
                    system.technologies.add(tech)
            
            # Add skills through SystemSkillGain
            for skill_name in sys_data.get('skills', []):
                skill = next((s for s in skills if s.name == skill_name), None)
                if skill:
                    SystemSkillGain.objects.create(
                        system=system,
                        skill=skill,
                        proficiency_gained=random.randint(1, 3),
                        learning_context=random.choice(['project', 'tutorial', 'documentation', 'experimentation']),
                        importance_level=random.randint(3, 5)
                    )
            
            # Add features
            for feature_text in sys_data.get('features', []):
                SystemFeature.objects.create(
                    system=system,
                    name=feature_text.split(':')[0] if ':' in feature_text else feature_text[:50],
                    description=feature_text,
                    is_core=random.choice([True, False]),
                    implementation_status='completed'
                )
            
            # Add challenges
            for challenge_text in sys_data.get('challenges', []):
                SystemChallenge.objects.create(
                    system=system,
                    title=challenge_text,
                    description=f"Detailed analysis and solution approach for: {challenge_text}",
                    challenge_type=random.choice(['technical', 'design', 'performance', 'integration']),
                    difficulty_level=random.randint(2, 4),
                    status='resolved',
                    resolution_notes=f"Successfully resolved through research and iterative development."
                )
            
            # Add metrics
            for metric_name, value in sys_data.get('metrics', {}).items():
                SystemMetric.objects.create(
                    system=system,
                    name=metric_name,
                    value=str(value),
                    unit='%' if 'Score' in metric_name or 'Coverage' in metric_name else 'ms' if 'Time' in metric_name else '',
                    metric_type='performance' if 'Score' in metric_name else 'technical',
                    last_updated=timezone.now()
                )
        
        systems.append(system)
    
    print(f"✅ Created {len(systems)} systems with features, challenges, and metrics")
    return systems

def create_blog_content(categories, tags, systems, users):
    """Create blog posts and series"""
    print("📝 Creating blog content...")
    
    # Create a series first
    series_data = {
        'title': 'Django Learning Journey',
        'slug': 'django-learning-journey',
        'description': '''Follow my comprehensive journey learning Django from scratch. Each post documents challenges, solutions, and insights gained while building real projects.

This series covers everything from initial setup through advanced topics like custom admin interfaces, performance optimization, and deployment strategies.''',
        'is_complete': False,
        'post_count': 0,
        'total_reading_time': 0,
        'is_featured': True
    }
    
    series, created = Series.objects.get_or_create(
        slug='django-learning-journey',
        defaults=series_data
    )
    
    posts_data = [
        {
            'title': 'Setting Up My Django Development Environment',
            'category': 'Development',
            'tags': ['python', 'django', 'tutorial', 'beginner'],
            'series': series,
            'series_order': 1,
            'content': '''# Setting Up My Django Development Environment

After deciding to dive deep into Django, I knew that having a solid development environment would be crucial for my learning success. Here's how I set everything up and the lessons I learned along the way.

## The Tools I Chose

### Python Environment Management
I decided to use `pyenv` for managing Python versions and `venv` for project-specific virtual environments. This combination gives me:
- Control over Python versions per project
- Isolated dependencies 
- Easy switching between projects

```python
# Creating a new project environment
python -m venv myproject_env
source myproject_env/bin/activate  # On Windows: myproject_env\\Scripts\\activate
pip install django
```

### Code Editor Setup
VS Code became my editor of choice with these essential extensions:
- Python extension for syntax highlighting and debugging
- Django extension for template syntax
- GitLens for version control visualization
- Auto-formatting with Black

### Database Choice
For development, I started with SQLite (Django's default) but quickly moved to PostgreSQL to match production environments. This decision saved me from database-specific gotchas later.

## Key Configuration Decisions

### Settings Organization
From the start, I organized settings into separate files:
- `base.py` - Common settings
- `development.py` - Local development overrides
- `production.py` - Production-specific settings

This pattern has served me well across multiple projects.

### Environment Variables
Using python-decouple to manage secrets and environment-specific settings:

```python
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
DATABASE_URL = config('DATABASE_URL')
```

## Lessons Learned

### Start with Production in Mind
Even for learning projects, I configured things like:
- Proper secret key management
- Database settings that match production
- Static file handling for deployment

### Version Control from Day One
Every Django project gets initialized with git immediately:
```bash
git init
# Add comprehensive .gitignore for Python/Django
git add .
git commit -m "Initial Django project setup"
```

### Documentation Habits
I started documenting setup steps in README.md files from the beginning. This habit has saved me countless hours when returning to projects or helping others.

## My Current Workflow

1. **Project Creation**: Use django-admin startproject with custom template
2. **Environment Setup**: Create virtual environment and install dependencies
3. **Database Setup**: Configure PostgreSQL and run initial migrations
4. **Version Control**: Initialize git and make initial commit
5. **Development**: Code with frequent commits and descriptive messages

## Tools That Made the Difference

- **Django Extensions**: Provides shell_plus, show_urls, and other utilities
- **Django Debug Toolbar**: Essential for understanding query performance
- **Pre-commit hooks**: Automatic code formatting and linting

## Next Steps

With my environment dialed in, I'm ready to dive into Django models and database design. Having these fundamentals solid gives me confidence to focus on learning Django concepts rather than fighting with setup issues.

The time invested in a proper development setup has paid dividends in productivity and learning speed.''',
            'featured_code': '''# settings/base.py
from decouple import config
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'django_extensions',
    'debug_toolbar',
    
    # Local apps
    'core',
    'blog',
    'projects',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]''',
            'featured_code_format': 'python',
            'reading_time': 8,
            'system_connections': ['AURA Portfolio System']
        },
        {
            'title': 'Building My First Django Model Relationships',
            'category': 'Development',
            'tags': ['django', 'models', 'database', 'learning'],
            'series': series,
            'series_order': 2,
            'content': '''# Building My First Django Model Relationships

Understanding Django model relationships was a crucial milestone in my learning journey. Coming from a background in environmental data analysis, I was familiar with relational concepts, but Django's ORM implementation had its own nuances to master.

## The Challenge: Portfolio Data Structure

For my portfolio project, I needed to model complex relationships between:
- Skills and Technologies
- Projects and their Technologies
- Blog posts connected to Projects
- User experience and skill development

## One-to-Many Relationships (ForeignKey)

The most straightforward relationship I implemented was connecting blog posts to categories:

```python
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    color = models.CharField(max_length=7, default="#26c6da")

class Post(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    content = models.TextField()
```

### Key Learning: on_delete Behavior
Understanding `on_delete` options was crucial:
- `CASCADE`: Delete posts when category is deleted
- `SET_NULL`: Keep posts, set category to null (requires null=True)
- `PROTECT`: Prevent category deletion if posts exist

## Many-to-Many Relationships

The relationship between projects and technologies required a many-to-many field:

```python
class Technology(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)

class SystemModule(models.Model):
    title = models.CharField(max_length=200)
    technologies = models.ManyToManyField(Technology, blank=True)
```

### Through Models for Additional Data

When I needed to track HOW skills were gained through projects, I used a through model:

```python
class SystemSkillGain(models.Model):
    system = models.ForeignKey(SystemModule, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency_gained = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    learning_context = models.CharField(max_length=50)
    
class SystemModule(models.Model):
    # ... other fields
    skills = models.ManyToManyField(Skill, through='SystemSkillGain')
```

## Complex Relationships: Blog Posts to Projects

One of my most interesting relationship challenges was connecting blog posts to multiple projects with metadata about the connection:

```python
class SystemLogEntry(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="system_connections")
    system = models.ForeignKey(SystemModule, on_delete=models.CASCADE, related_name="log_entries")
    connection_type = models.CharField(max_length=20, choices=CONNECTION_TYPES)
    priority = models.IntegerField(choices=PRIORITY_LEVELS)
    log_entry_id = models.CharField(max_length=20, blank=True)
```

This allows me to:
- Link blog posts to multiple projects
- Categorize the type of connection (development, documentation, analysis)
- Set priority levels for display ordering
- Generate HUD-style identifiers for the tech theme

## Query Optimization Lessons

As my data grew, I learned about query optimization:

### select_related for ForeignKey
```python
# Efficient: One database query
posts = Post.objects.select_related('category', 'author').all()

# Inefficient: N+1 queries
posts = Post.objects.all()  # Then accessing post.category triggers more queries
```

### prefetch_related for Many-to-Many
```python
# Efficient: Two queries total
systems = SystemModule.objects.prefetch_related('technologies', 'skills').all()
```

## Admin Interface Integration

Django's admin interface made testing relationships intuitive:

```python
class SystemModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'system_type', 'status', 'get_tech_count']
    filter_horizontal = ['technologies']  # Nice UI for many-to-many
    
    def get_tech_count(self, obj):
        return obj.technologies.count()
    get_tech_count.short_description = 'Technologies'
```

## Migration Strategies

I learned to think carefully about migrations when changing relationships:

1. **Adding relationships**: Usually straightforward
2. **Removing relationships**: Consider data preservation
3. **Changing relationship types**: Often requires custom migration

## Debugging Relationship Issues

The Django shell became my best friend for understanding relationships:

```python
# In Django shell
from projects.models import SystemModule

system = SystemModule.objects.first()
print(system.technologies.all())  # Forward relationship
print(system.log_entries.all())   # Reverse relationship via related_name
```

## Lessons Learned

1. **Plan relationships carefully**: Draw diagrams before coding
2. **Use descriptive related_names**: Makes reverse lookups clear
3. **Consider query performance**: Use select_related and prefetch_related
4. **Through models are powerful**: Don't avoid them when you need metadata
5. **Test in Django shell**: Interactive testing reveals relationship behavior

## Next Steps

With solid model relationships in place, I'm ready to build views that efficiently query and display this interconnected data. The foundation of proper relationships makes everything else easier.

Understanding these patterns has made me more confident in database design and opened up possibilities for rich, interconnected applications.''',
            'featured_code': '''class SystemLogEntry(models.Model):
    """Connection between blog posts and systems with HUD metadata"""
    CONNECTION_TYPES = (
        ("development", "Development Log"),
        ("documentation", "Technical Documentation"), 
        ("analysis", "System Analysis"),
        ("troubleshooting", "Troubleshooting"),
    )
    
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="system_connections"
    )
    system = models.ForeignKey(
        SystemModule, on_delete=models.CASCADE, related_name="log_entries"  
    )
    connection_type = models.CharField(max_length=20, choices=CONNECTION_TYPES)
    priority = models.IntegerField(choices=[(i, i) for i in range(1, 5)])
    log_entry_id = models.CharField(max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('post', 'system')
        ordering = ['-priority', '-created_at']
    
    def save(self, *args, **kwargs):
        if not self.log_entry_id:
            self.log_entry_id = f"SYS-{self.system.pk:03d}-LOG-{self.pk or 999:03d}"
        super().save(*args, **kwargs)''',
            'featured_code_format': 'python',
            'reading_time': 12,
            'system_connections': ['AURA Portfolio System', 'Task Management API']
        },
        {
            'title': 'Debugging My First Complex Django Query Issue',
            'category': 'Analysis',
            'tags': ['django', 'debugging', 'database', 'performance', 'problem-solving'],
            'content': '''# Debugging My First Complex Django Query Issue

Yesterday I encountered my most challenging Django performance problem yet. What started as a simple feature request turned into a deep dive into query optimization, N+1 problems, and the Django Debug Toolbar. Here's how I solved it and what I learned.

## The Problem: Slow Dashboard Loading

My portfolio dashboard was taking 15+ seconds to load. The page displays:
- Recent blog posts with their connected systems
- System metrics and status indicators  
- Skill progression data with project connections

What should have been a quick overview page became unusable.

## Investigation Phase

### Django Debug Toolbar to the Rescue

The Debug Toolbar immediately showed the problem: **847 database queries** for a single page load. Classic N+1 query problem.

```python
# The problematic code in my view
def dashboard_view(request):
    posts = Post.objects.filter(status='published')[:5]
    systems = SystemModule.objects.filter(status='published')
    
    context = {
        'posts': posts,
        'systems': systems,
        # ... more context
    }
    return render(request, 'dashboard.html', context)
```

### Template Analysis

The template was innocently accessing related objects:

```html
<!-- This triggered queries for EVERY post -->
{% for post in posts %}
    <h3>{{ post.title }}</h3>
    <p>Category: {{ post.category.name }}</p>  <!-- Query! -->
    <p>Author: {{ post.author.username }}</p>  <!-- Query! -->
    {% for connection in post.system_connections.all %}  <!-- Query per post! -->
        <span>{{ connection.system.title }}</span>  <!-- Query per connection! -->
    {% endfor %}
{% endfor %}
```

Every template access triggered a separate database query.

## The Solution: Strategic Query Optimization

### Step 1: select_related for ForeignKey relationships

```python
# Fixed the single-valued relationships
posts = Post.objects.select_related('category', 'author').filter(
    status='published'
)[:5]
```

This reduced queries from 15 (3 per post × 5 posts) to 1.

### Step 2: prefetch_related for Many-to-Many and reverse ForeignKeys

```python
# Fixed the system connections
posts = Post.objects.select_related('category', 'author').prefetch_related(
    'system_connections__system'
).filter(status='published')[:5]
```

The `system_connections__system` prefetch follows the relationship through the junction model to get the related system data.

### Step 3: Complex Prefetching for System Data

The systems data needed multiple levels of related objects:

```python
systems = SystemModule.objects.select_related('system_type').prefetch_related(
    'technologies',
    'skills',
    'log_entries__post',  # Reverse relationship through SystemLogEntry
    'metrics',
    'challenges'
).filter(status='published')
```

## Advanced Optimization Techniques

### Custom Queryset Methods

I created reusable queryset methods for common access patterns:

```python
class PostQuerySet(models.QuerySet):
    def with_relations(self):
        return self.select_related('category', 'author').prefetch_related(
            'tags',
            'system_connections__system__system_type'
        )
    
    def published(self):
        return self.filter(status='published')

class Post(models.Model):
    # ... model fields
    
    objects = PostQuerySet.as_manager()

# Usage in views
posts = Post.objects.published().with_relations()[:5]
```

### Annotation for Computed Values

Instead of calculating counts in templates, I moved them to the database:

```python
from django.db.models import Count

systems = SystemModule.objects.annotate(
    tech_count=Count('technologies'),
    log_count=Count('log_entries')
).select_related('system_type')
```

Template usage became simple and efficient:
```html
<p>{{ system.tech_count }} technologies used</p>  <!-- No query! -->
```

## Testing the Performance Improvements

### Before Optimization
- **Query Count**: 847 queries
- **Load Time**: 15.2 seconds
- **Memory Usage**: 145MB

### After Optimization  
- **Query Count**: 8 queries
- **Load Time**: 0.3 seconds
- **Memory Usage**: 12MB

## Key Lessons Learned

### 1. Template Access Patterns Matter
Every dot notation in templates can trigger queries. Plan template data access when designing views.

### 2. Use Debug Toolbar Early
Don't wait for performance problems. Install and use Django Debug Toolbar from the start of development.

### 3. Understand Relationship Types
- **select_related**: Use for ForeignKey and OneToOne (SQL JOINs)
- **prefetch_related**: Use for ManyToMany and reverse ForeignKey (separate queries)

### 4. Prefetch Through Relationships
You can prefetch through multiple relationship levels:
```python
'system_connections__system__technologies'  # Three levels deep
```

### 5. Database-Level Calculations
Move counting and aggregation to the database with `annotate()` rather than Python loops.

## Debugging Tools That Helped

1. **Django Debug Toolbar**: Query analysis and timing
2. **Django Extensions shell_plus**: Interactive query testing
3. **PostgreSQL EXPLAIN**: Understanding actual query execution
4. **Python cProfile**: Finding Python-level bottlenecks

## Testing Queries Interactively

The Django shell became essential for testing optimizations:

```python
# Test query efficiency
from django.test.utils import override_settings
from django.db import connection

# Enable query logging
with override_settings(DEBUG=True):
    posts = Post.objects.with_relations()[:5]
    for post in posts:
        print(f"{post.title} - {post.category.name}")
        for conn in post.system_connections.all():
            print(f"  -> {conn.system.title}")
    
    print(f"Query count: {len(connection.queries)}")
```

## Going Forward

This experience taught me to think about database efficiency from the start rather than optimizing after problems appear. I now:

1. Use select_related/prefetch_related in initial view design
2. Test with realistic data volumes early
3. Monitor query counts as a key metric
4. Create reusable queryset methods for common patterns

Performance optimization in Django isn't just about making things faster—it's about understanding the relationship between your Python code, the ORM, and the underlying database. This debugging session was frustrating at first, but it significantly leveled up my Django skills.

The dashboard now loads instantly, and I have a solid framework for avoiding similar issues in future projects.''',
            'featured_code': '''# Optimized dashboard view with efficient querying
class DashboardView(TemplateView):
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Efficiently load posts with all related data
        recent_posts = Post.objects.select_related(
            'category', 'author'
        ).prefetch_related(
            'tags',
            'system_connections__system__system_type'
        ).filter(status='published')[:5]
        
        # Load systems with annotations for computed values
        featured_systems = SystemModule.objects.select_related(
            'system_type'
        ).prefetch_related(
            'technologies', 'skills'
        ).annotate(
            tech_count=Count('technologies'),
            log_count=Count('log_entries', filter=Q(log_entries__post__status='published'))
        ).filter(
            is_featured=True, status='published'
        )[:3]
        
        context.update({
            'recent_posts': recent_posts,
            'featured_systems': featured_systems,
            'total_queries': len(connection.queries),  # For debugging
        })
        
        return context''',
            'featured_code_format': 'python',
            'reading_time': 15,
            'system_connections': ['AURA Portfolio System']
        },
        {
            'title': 'From Environmental Data to Django: Applying Domain Knowledge',
            'category': 'Learning',
            'tags': ['career-change', 'data-analysis', 'python', 'learning', 'self-taught'],
            'content': '''# From Environmental Data to Django: Applying Domain Knowledge

One of the unexpected advantages of transitioning from Environmental Health to software development has been how directly my domain expertise translates to programming concepts. Today I want to share how my background in environmental data analysis shaped my approach to learning Django and building applications.

## The Data Analysis Connection

### Environmental Health Background
In my previous role, I regularly worked with:
- Large datasets of air quality measurements
- Water contamination testing results  
- Regulatory compliance tracking
- Statistical analysis for trend identification
- Risk assessment modeling

### Django Translation
These skills map surprisingly well to web development:
- **Dataset handling** → Database design and ORM queries
- **Data validation** → Form validation and input sanitization  
- **Regulatory compliance** → Security best practices and data protection
- **Statistical analysis** → Aggregation queries and reporting features
- **Risk assessment** → Error handling and edge case planning

## Building My Environmental Data Analyzer

To bridge these worlds, I built a Django application that processes environmental monitoring data—combining my domain knowledge with new programming skills.

### The Challenge: Messy Real-World Data

Environmental data is notoriously messy:
```python
# Typical air quality dataset issues
raw_data = {
    'PM2.5': ['15.6', 'N/A', '22.1', '-999', '18.3'],  # Mixed types, missing values, error codes
    'Date': ['2023-01-01', '01/02/2023', '2023-1-3'],  # Inconsistent date formats
    'Location': ['Site A ', 'site b', 'SITE C'],        # Inconsistent naming/casing
}
```

This messy data taught me valuable lessons about defensive programming and data validation—skills that apply to any Django application.

### Django Models for Environmental Data

```python
class MonitoringSite(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    site_type = models.CharField(max_length=50, choices=SITE_TYPE_CHOICES)
    active = models.BooleanField(default=True)

class AirQualityMeasurement(models.Model):
    site = models.ForeignKey(MonitoringSite, on_delete=models.CASCADE)
    measurement_date = models.DateTimeField()
    pm25 = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    pm10 = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    ozone = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Data quality indicators
    is_validated = models.BooleanField(default=False)
    quality_flag = models.CharField(max_length=20, choices=QUALITY_CHOICES)
    notes = models.TextField(blank=True)
```

## Domain Knowledge as a Learning Accelerator

### Understanding Relationships Naturally
Environmental data has natural relationships that made Django model relationships intuitive:
- Sites have many measurements (One-to-Many)
- Measurements can have multiple pollutants (related fields)
- Regulations apply to multiple sites (Many-to-Many)

### Real-World Complexity from Day One
Because I understood the domain complexity, I could focus on learning Django rather than figuring out what to build. I immediately needed:
- Data validation and error handling
- Complex queries and filtering
- Statistical aggregations
- Data visualization
- Report generation

## Practical Django Skills from Environmental Work

### 1. Data Validation Patterns
Environmental data taught me to never trust input:

```python
class AirQualityForm(forms.ModelForm):
    def clean_pm25(self):
        value = self.cleaned_data['pm25']
        if value is not None:
            if value < 0:
                raise ValidationError("PM2.5 cannot be negative")
            if value > 500:  # Extremely high value, likely error
                raise ValidationError("PM2.5 value seems unrealistic")
        return value
```

### 2. Aggregation and Reporting
Environmental work requires lots of statistical summaries:

```python
# Django ORM for environmental statistics
monthly_averages = AirQualityMeasurement.objects.filter(
    measurement_date__year=2023
).annotate(
    month=TruncMonth('measurement_date')
).values('month', 'site__name').annotate(
    avg_pm25=Avg('pm25'),
    max_pm25=Max('pm25'),
    measurement_count=Count('id')
).order_by('month', 'site__name')
```

### 3. Complex Filtering and Search
Environmental professionals need to slice data many ways:

```python
class MeasurementFilter:
    def filter_by_criteria(self, queryset, criteria):
        if criteria.get('date_range'):
            start, end = criteria['date_range']
            queryset = queryset.filter(measurement_date__range=(start, end))
        
        if criteria.get('site_types'):
            queryset = queryset.filter(site__site_type__in=criteria['site_types'])
        
        if criteria.get('quality_assured'):
            queryset = queryset.filter(is_validated=True)
        
        return queryset
```

## Building Confidence Through Familiar Problems

### Starting With What I Know
Instead of building generic tutorial projects, I immediately tackled problems I understood:
- Data import and cleaning workflows
- Statistical analysis and visualization
- Regulatory compliance tracking
- Report generation

This approach had several benefits:
- **Faster learning**: I could focus on Django concepts rather than domain logic
- **Real motivation**: Solving actual problems I'd faced before
- **Natural complexity**: Real-world messiness from the start
- **Portfolio relevance**: Demonstrated both technical skills and domain expertise

### Transferable Problem-Solving Patterns
Environmental work taught me systematic approaches that apply perfectly to debugging Django applications:

1. **Isolate the problem**: Same approach for contamination sources and code bugs
2. **Check data quality**: Environmental measurements and user input both need validation
3. **Test incrementally**: Scientific method applies to code testing
4. **Document everything**: Laboratory notebooks → code comments and documentation

## Advice for Career Changers

### 1. Leverage Your Domain Knowledge
Don't abandon your previous expertise—use it as a learning accelerator:
- Build applications that solve problems you understand
- Use your domain for realistic test data and scenarios
- Demonstrate unique value by combining technical and domain skills

### 2. Translate, Don't Start Over
Look for concepts that translate:
- **Data analysis** → Database queries and aggregations
- **Process documentation** → Code documentation and testing
- **Quality assurance** → Input validation and error handling
- **Stakeholder communication** → User experience and interface design

### 3. Build a Bridge Portfolio
Create projects that showcase both your new technical skills and existing domain knowledge. This combination makes you uniquely valuable.

## Looking Forward

My environmental health background didn't slow down my Django learning—it accelerated it. By building applications that solve real problems I understand, I've been able to focus on learning Django concepts while creating genuinely useful tools.

The combination of technical skills and domain expertise is powerful. Employers value developers who can not only write code, but also understand the business problems the code needs to solve.

For fellow career changers: your previous experience isn't baggage—it's your competitive advantage. Use it wisely and you'll learn faster and stand out from the crowd.''',
            'reading_time': 18,
            'system_connections': ['Environmental Data Analyzer']
        },
        {
            'title': 'Custom Django Admin: Beyond the Basics',
            'category': 'Tutorial',
            'tags': ['django', 'admin', 'customization', 'tutorial'],
            'content': '''# Custom Django Admin: Beyond the Basics

Django's admin interface is powerful out of the box, but customizing it to match your application's specific needs can dramatically improve your content management experience. Here's what I learned while building a custom admin for my portfolio system.

## The Challenge: HUD-Style Admin Interface

My portfolio site has a futuristic HUD theme, and the default Django admin felt disconnected from that aesthetic. I needed:
- Custom styling that matched the site theme
- Bulk operations for managing content
- Dashboard views with key metrics
- Simplified workflows for common tasks

## Admin Customization Levels

### Level 1: Basic ModelAdmin Configuration

```python
@admin.register(SystemModule)
class SystemModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'system_type', 'status', 'complexity', 'get_tech_count']
    list_filter = ['status', 'system_type', 'complexity', 'is_featured']
    search_fields = ['title', 'subtitle', 'description']
    list_editable = ['status', 'is_featured']
    
    def get_tech_count(self, obj):
        return obj.technologies.count()
    get_tech_count.short_description = 'Technologies'
```

### Level 2: Custom Templates and Styling

Created `admin/base_site.html` to override default styling:

```html
{% extends "admin/base.html" %}
{% load static %}

{% block title %}AURA Admin{% endblock %}

{% block extrahead %}
{{ block.super }}
<link rel="stylesheet" href="{% static 'admin/css/custom_admin.css' %}">
{% endblock %}

{% block branding %}
<h1 class="admin-title">
    <i class="fas fa-terminal"></i>
    AURA ADMIN INTERFACE
</h1>
{% endblock %}
```

### Level 3: Custom Admin Views

Built completely custom admin views that extend Django's base admin functionality:

```python
class BaseAdminView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Base class for custom admin views with consistent styling"""
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'site_title': 'AURA Admin',
            'site_header': 'AURA Portfolio Admin',
            'has_permission': True,
        })
        return context

class SystemDashboardView(BaseAdminView, TemplateView):
    template_name = 'admin/systems_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Dashboard statistics
        context.update({
            'total_systems': SystemModule.objects.count(),
            'published_systems': SystemModule.objects.filter(status='published').count(),
            'recent_systems': SystemModule.objects.order_by('-created_at')[:5],
            'technology_stats': self.get_technology_stats(),
        })
        
        return context
    
    def get_technology_stats(self):
        return Technology.objects.annotate(
            system_count=Count('systemmodule')
        ).order_by('-system_count')[:10]
```

## Advanced Customization Techniques

### 1. Bulk Actions for Efficiency

```python
def make_published(modeladmin, request, queryset):
    updated = queryset.update(status='published')
    modeladmin.message_user(
        request, 
        f'{updated} systems were successfully published.'
    )
make_published.short_description = "Mark selected systems as published"

def bulk_add_technology(modeladmin, request, queryset):
    # Custom bulk operation with form
    if 'apply' in request.POST:
        form = BulkTechnologyForm(request.POST)
        if form.is_valid():
            technology = form.cleaned_data['technology']
            for system in queryset:
                system.technologies.add(technology)
            # Success message...
        return HttpResponseRedirect(request.get_full_path())
    
    form = BulkTechnologyForm()
    return render(request, 'admin/bulk_technology.html', {
        'form': form,
        'systems': queryset,
    })

class SystemModuleAdmin(admin.ModelAdmin):
    actions = [make_published, bulk_add_technology]
```

### 2. Custom Filters

```python
class StatusFilter(admin.SimpleListFilter):
    title = 'Status Category'
    parameter_name = 'status_category'
    
    def lookups(self, request, model_admin):
        return [
            ('active', 'Active Projects'),
            ('complete', 'Completed Projects'),
            ('learning', 'Learning Projects'),
        ]
    
    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(status__in=['in_development', 'testing'])
        elif self.value() == 'complete':
            return queryset.filter(status__in=['deployed', 'published'])
        elif self.value() == 'learning':
            return queryset.filter(system_type__name='Learning Project')
```

### 3. Inline Editing for Related Objects

```python
class SystemFeatureInline(admin.TabularInline):
    model = SystemFeature
    extra = 1
    fields = ['name', 'description', 'is_core', 'implementation_status']

class SystemChallengeInline(admin.StackedInline):
    model = SystemChallenge
    extra = 0
    fields = ['title', 'description', 'difficulty_level', 'status']

class SystemModuleAdmin(admin.ModelAdmin):
    inlines = [SystemFeatureInline, SystemChallengeInline]
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['title', 'subtitle', 'system_type', 'status']
        }),
        ('Content', {
            'fields': ['description', 'github_url', 'demo_url'],
            'classes': ['wide']
        }),
        ('Metadata', {
            'fields': ['complexity', 'priority', 'is_featured'],
            'classes': ['collapse']
        }),
    ]
```

## JavaScript Enhancements

Added custom JavaScript for better user experience:

```javascript
// admin/js/custom_admin.js
(function($) {
    $(document).ready(function() {
        // Auto-generate slug from title
        $('#id_title').on('input', function() {
            var title = $(this).val();
            var slug = title.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
            $('#id_slug').val(slug);
        });
        
        // Confirmation for bulk actions
        $('.button').click(function() {
            var action = $('select[name="action"]').val();
            if (action && action.includes('delete')) {
                return confirm('Are you sure you want to perform this action?');
            }
        });
        
        // Status color coding
        $('.field-status').each(function() {
            var status = $(this).text().trim();
            $(this).addClass('status-' + status.toLowerCase());
        });
    });
})(django.jQuery);
```

## Custom Dashboard Widgets

Created reusable dashboard widgets for key metrics:

```python
def admin_dashboard_view(request):
    """Custom admin dashboard with portfolio-specific metrics"""
    
    # System statistics
    systems_by_status = SystemModule.objects.values('status').annotate(
        count=Count('id')
    )
    
    # Technology usage
    tech_usage = Technology.objects.annotate(
        usage_count=Count('systemmodule')
    ).filter(usage_count__gt=0).order_by('-usage_count')
    
    # Recent activity
    recent_posts = Post.objects.select_related('category').order_by('-created_at')[:5]
    recent_systems = SystemModule.objects.order_by('-updated_at')[:5]
    
    context = {
        'systems_by_status': systems_by_status,
        'tech_usage': tech_usage,
        'recent_posts': recent_posts,
        'recent_systems': recent_systems,
        'title': 'Portfolio Dashboard',
    }
    
    return render(request, 'admin/dashboard.html', context)
```

## Testing Admin Customizations

```python
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class AdminCustomizationTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            'admin', 'admin@test.com', 'password'
        )
        self.client = Client()
        self.client.login(username='admin', password='password')
    
    def test_custom_dashboard_view(self):
        response = self.client.get(reverse('admin:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Portfolio Dashboard')
    
    def test_bulk_actions(self):
        # Create test systems
        systems = [SystemModule.objects.create(title=f'System {i}') for i in range(3)]
        
        # Test bulk publish action
        data = {
            'action': 'make_published',
            '_selected_action': [s.pk for s in systems],
        }
        response = self.client.post(reverse('admin:projects_systemmodule_changelist'), data)
        
        # Verify systems were published
        for system in systems:
            system.refresh_from_db()
            self.assertEqual(system.status, 'published')
```

## Key Lessons Learned

### 1. Start Simple, Build Up
Begin with basic `ModelAdmin` customizations before building custom views.

### 2. Maintain Django Patterns
Custom admin views should still feel like Django admin—consistent navigation, permissions, and styling.

### 3. Focus on Workflows
Design admin customizations around actual content management workflows, not just aesthetics.

### 4. Test Everything
Custom admin functionality needs thorough testing, especially bulk operations and custom views.

### 5. Document Power User Features
Complex admin customizations should be documented for other team members.

## Results

The custom admin interface dramatically improved my content management efficiency:
- **75% faster** content creation with better workflows
- **90% fewer clicks** for common operations through bulk actions
- **Better overview** of system status with dashboard metrics
- **Consistent theming** that matches the site's aesthetic

Custom Django admin isn't just about pretty interfaces—it's about creating tools that match how you actually work with your data. The time invested in thoughtful admin customization pays dividends in daily productivity.''',
            'featured_code': '''class SystemModuleAdmin(admin.ModelAdmin):
    """Enhanced admin for SystemModule with custom features"""
    
    list_display = [
        'title', 'system_type', 'colored_status', 'complexity_display', 
        'get_tech_count', 'is_featured', 'updated_at'
    ]
    list_filter = ['status', 'system_type', 'complexity', 'is_featured', StatusFilter]
    search_fields = ['title', 'subtitle', 'description']
    list_editable = ['is_featured']
    actions = ['make_published', 'make_featured', 'bulk_add_technology']
    
    fieldsets = [
        ('System Information', {
            'fields': ['title', 'subtitle', 'system_id', 'system_type']
        }),
        ('Status & Priority', {
            'fields': ['status', 'complexity', 'priority', 'is_featured'],
            'classes': ['wide']
        }),
        ('Content', {
            'fields': ['description', 'usage_examples', 'setup_instructions'],
            'classes': ['wide']
        }),
        ('Links & Resources', {
            'fields': ['github_url', 'demo_url', 'documentation_url'],
            'classes': ['collapse']
        }),
    ]
    
    inlines = [SystemFeatureInline, SystemChallengeInline, SystemMetricInline]
    
    def colored_status(self, obj):
        colors = {
            'draft': '#6c757d',
            'in_development': '#ffc107', 
            'deployed': '#28a745',
            'published': '#007bff'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    colored_status.short_description = 'Status'
    
    def complexity_display(self, obj):
        stars = '★' * obj.complexity + '☆' * (5 - obj.complexity)
        return format_html('<span title="Complexity: {}/5">{}</span>', obj.complexity, stars)
    complexity_display.short_description = 'Complexity'
    
    def get_tech_count(self, obj):
        count = obj.technologies.count()
        return format_html('<span class="tech-count">{}</span>', count)
    get_tech_count.short_description = 'Tech Stack'
    
    class Media:
        css = {'all': ('admin/css/custom_system_admin.css',)}
        js = ('admin/js/system_admin.js',)''',
            'featured_code_format': 'python',
            'reading_time': 20,
            'system_connections': ['AURA Portfolio System']
        }
    ]
    
    # Create posts and series relationships
    posts = []
    for i, post_data in enumerate(posts_data, 1):
        # Find category and author
        category = next((c for c in categories if c.name == post_data['category']), categories[0])
        author = users[0]  # Admin user as author
        
        # Create post
        post_fields = {
            'title': post_data['title'],
            'content': post_data['content'],
            'excerpt': post_data['content'][:200] + '...',
            'category': category,
            'author': author,
            'status': 'published',
            'featured': i <= 2,  # First 2 posts are featured
            'reading_time': post_data.get('reading_time', 10),
            'featured_code': post_data.get('featured_code', ''),
            'featured_code_format': post_data.get('featured_code_format', ''),
            'created_at': timezone.now() - timedelta(days=30-i*5),
            'published_at': timezone.now() - timedelta(days=30-i*5),
        }
        
        post, created = Post.objects.get_or_create(
            title=post_data['title'],
            defaults=post_fields
        )
        
        if created:
            # Add tags
            for tag_name in post_data.get('tags', []):
                tag = next((t for t in tags if t.name == tag_name), None)
                if tag:
                    post.tags.add(tag)
            
            # Add to series if specified
            if 'series' in post_data:
                SeriesPost.objects.create(
                    series=post_data['series'],
                    post=post,
                    order=post_data.get('series_order', i)
                )
            
            # Connect to systems
            for system_title in post_data.get('system_connections', []):
                system = next((s for s in systems if s.title == system_title), None)
                if system:
                    SystemLogEntry.objects.create(
                        post=post,
                        system=system,
                        connection_type=random.choice(['development', 'documentation', 'analysis']),
                        priority=random.randint(2, 4),
                        log_entry_id=f"SYS-{system.pk:03d}-LOG-{post.pk:03d}"
                    )
        
        posts.append(post)
    
    # Update series post count
    if series:
        series.update_metrics()
    
    print(f"✅ Created {len(posts)} blog posts with connections")
    return posts, series

def create_comments_and_views(posts, users):
    """Create sample comments and page views"""
    print("💬 Creating comments and views...")
    
    # Sample comments
    comment_texts = [
        "Great explanation of Django model relationships! This helped me understand the through model concept.",
        "Thanks for sharing your debugging process. The Django Debug Toolbar is such a powerful tool.",
        "Really appreciate seeing the career change perspective. I'm making a similar transition.",
        "The code examples are super helpful. Going to try implementing something similar.",
        "Love the detailed breakdown of the optimization process. Performance matters!",
        "Your environmental data background gives you a unique perspective on data handling.",
        "This is exactly what I needed for my current project. Thanks for the thorough tutorial!",
        "The admin customization tips are gold. Django's admin is so powerful when you dig deeper.",
    ]
    
    comments = []
    views = []
    
    for post in posts:
        # Add 2-5 comments per post
        num_comments = random.randint(2, 5)
        for i in range(num_comments):
            comment, created = Comment.objects.get_or_create(
                post=post,
                name=f"User {i+1}",
                defaults={
                    'email': f"user{i+1}@example.com",
                    'content': random.choice(comment_texts),
                    'approved': True,
                    'created_at': timezone.now() - timedelta(days=random.randint(1, 20))
                }
            )
            comments.append(comment)
        
        # Add page views (10-50 per post)
        num_views = random.randint(10, 50)
        for i in range(num_views):
            ip = f"192.168.1.{random.randint(1, 254)}"
            view, created = PostView.objects.get_or_create(
                post=post,
                ip_address=ip,
                defaults={
                    'viewed_on': timezone.now() - timedelta(days=random.randint(1, 25))
                }
            )
            views.append(view)
    
    print(f"✅ Created {len(comments)} comments and {len(views)} page views")
    return comments, views

def create_contacts():
    """Create sample contact form submissions"""
    print("📧 Creating contact submissions...")
    
    contacts_data = [
        {
            'name': 'Sarah Johnson',
            'email': 'sarah.johnson@techcorp.com',
            'subject': 'Junior Developer Position',
            'message': '''Hi! I came across your portfolio and I'm impressed with your Django projects and your unique background in Environmental Health. We have a junior developer position that might be a great fit.

Would you be interested in discussing this opportunity? We're particularly looking for someone with strong analytical skills and Python experience.

Best regards,
Sarah Johnson
Tech Recruitment Specialist''',
            'inquiry_category': 'hiring',
            'priority': 'high',
            'is_read': True,
            'response_sent': True,
        },
        {
            'name': 'Mike Chen',
            'email': 'mike.chen@freelancer.dev',
            'subject': 'Collaboration on Environmental Data Project',
            'message': '''Hello! I saw your environmental data analyzer project and I'm working on something similar for a client in the renewable energy space.

Would you be interested in collaborating? I think your domain expertise combined with your Django skills would be incredibly valuable.

Looking forward to hearing from you!
Mike''',
            'inquiry_category': 'collaboration',
            'priority': 'normal',
            'is_read': True,
            'response_sent': False,
        },
        {
            'name': 'Jennifer Martinez',
            'email': 'jennifer.m@example.com',
            'subject': 'Question about Django Model Relationships',
            'message': '''Hi! I read your blog post about Django model relationships and I have a question about through models.

How do you handle validation when the through model has its own fields? I'm running into some issues with my current project.

Thanks for any insight you can provide!
Jen''',
            'inquiry_category': 'question',
            'priority': 'normal',
            'is_read': False,
            'response_sent': False,
        },
        {
            'name': 'Alex Rivera',
            'email': 'alex.rivera@startup.io',
            'subject': 'Portfolio Feedback',
            'message': '''Fantastic portfolio! Your project documentation is excellent and I love the HUD theme.

As someone who's also transitioning careers, your journey is really inspiring. Keep up the great work!''',
            'inquiry_category': 'feedback',
            'priority': 'low',
            'is_read': True,
            'response_sent': True,
        },
    ]
    
    contacts = []
    for contact_data in contacts_data:
        contact, created = Contact.objects.get_or_create(
            email=contact_data['email'],
            subject=contact_data['subject'],
            defaults={
                'name': contact_data['name'],
                'message': contact_data['message'],
                'inquiry_category': contact_data['inquiry_category'],
                'priority': contact_data['priority'],
                'is_read': contact_data['is_read'],
                'response_sent': contact_data['response_sent'],
                'created_at': timezone.now() - timedelta(days=random.randint(1, 30)),
                'response_date': timezone.now() - timedelta(days=random.randint(1, 15)) if contact_data['response_sent'] else None,
                'referrer_page': random.choice(['/projects/', '/blog/', '/about/', '/']),
                'ip_address': f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            }
        )
        contacts.append(contact)
    
    print(f"✅ Created {len(contacts)} contact submissions")
    return contacts

def create_portfolio_analytics():
    """Create portfolio analytics data"""
    print("📊 Creating portfolio analytics...")
    
    analytics_records = []
    
    # Create 90 days of analytics data
    for i in range(90):
        date_record = timezone.now().date() - timedelta(days=i)
        
        # Base values with some realistic patterns
        base_visitors = 15 + random.randint(-5, 10)
        base_pageviews = base_visitors * random.randint(2, 5)
        
        # Weekend traffic is typically lower
        if date_record.weekday() >= 5:  # Saturday/Sunday
            base_visitors = int(base_visitors * 0.7)
            base_pageviews = int(base_pageviews * 0.7)
        
        # Some days have viral posts or higher traffic
        if random.random() < 0.1:  # 10% chance of high traffic day
            base_visitors *= 3
            base_pageviews *= 3
        
        analytics_data = {
            'date': date_record,
            'unique_visitors': max(1, base_visitors),
            'page_views': max(1, base_pageviews),
            'datalog_views': random.randint(5, 25),
            'system_views': random.randint(8, 30),
            'contact_form_submissions': random.randint(0, 2),
            'github_clicks': random.randint(2, 15),
            'resume_downloads': random.randint(0, 3),
            'learning_hours_logged': round(random.uniform(2.0, 8.0), 1),
            'datalog_entries_written': random.randint(0, 1),
            'skills_practiced': random.randint(2, 6),
            'projects_worked_on': random.randint(1, 3),
            'milestones_achieved': random.randint(0, 2) if random.random() < 0.3 else 0,
        }
        
        analytics, created = PortfolioAnalytics.objects.get_or_create(
            date=date_record,
            defaults=analytics_data
        )
        analytics_records.append(analytics)
    
    print(f"✅ Created {len(analytics_records)} analytics records")
    return analytics_records

def create_skill_technology_relations(skills, technologies):
    """Create relationships between skills and technologies"""
    print("🔗 Creating skill-technology relationships...")
    
    # Define logical relationships
    skill_tech_mappings = {
        'Python': ['Python', 'Django', 'Pandas'],
        'Django': ['Django', 'Python', 'PostgreSQL'],
        'JavaScript': ['JavaScript', 'React', 'VS Code'],
        'HTML/CSS': ['HTML5', 'CSS3', 'Bootstrap', 'Tailwind CSS'],
        'PostgreSQL': ['PostgreSQL', 'SQL'],
        'Git/GitHub': ['Git'],
        'Data Analysis': ['Python', 'Pandas', 'Matplotlib'],
        'Problem Solving': ['Python', 'Git', 'VS Code'],
        'Technical Writing': ['VS Code'],
    }
    
    relationships = []
    
    for skill_name, tech_names in skill_tech_mappings.items():
        skill = next((s for s in skills if s.name == skill_name), None)
        if not skill:
            continue
            
        for tech_name in tech_names:
            technology = next((t for t in technologies if t.name == tech_name), None)
            if not technology:
                continue
                
            # Determine relationship strength
            if skill_name == 'Python' and tech_name == 'Python':
                proficiency_level = 4  # Core technology
            elif skill_name == tech_name:
                proficiency_level = 4  # Direct match
            elif tech_name in ['Django', 'PostgreSQL'] and skill_name in ['Python', 'Django']:
                proficiency_level = 3  # Strong relationship
            else:
                proficiency_level = 2  # Supporting technology
            
            relationship, created = SkillTechnologyRelation.objects.get_or_create(
                skill=skill,
                technology=technology,
                defaults={
                    'proficiency_level': proficiency_level,
                    'relationship_type': 'primary' if proficiency_level >= 4 else 'supporting',
                    'learning_notes': f"Gained {skill_name} experience primarily through {tech_name} projects.",
                    'date_started': timezone.now().date() - timedelta(days=random.randint(180, 730)),
                    'projects_count': random.randint(1, 5),
                }
            )
            relationships.append(relationship)
    
    print(f"✅ Created {len(relationships)} skill-technology relationships")
    return relationships

def create_architecture_components(systems, technologies):
    """Create architecture components and connections"""
    print("🏗️ Creating architecture components...")
    
    components = []
    connections = []
    
    # Create components for each system
    for system in systems:
        if system.title == 'AURA Portfolio System':
            # Portfolio system components
            component_data = [
                {'name': 'Django Backend', 'type': 'backend', 'tech': 'Django', 'pos': (0, 0, 0), 'color': '#092e20'},
                {'name': 'PostgreSQL Database', 'type': 'database', 'tech': 'PostgreSQL', 'pos': (-2, -1, 0), 'color': '#336791'},
                {'name': 'Frontend Interface', 'type': 'frontend', 'tech': 'HTML5', 'pos': (0, 2, 0), 'color': '#e34c26'},
                {'name': 'Admin Interface', 'type': 'backend', 'tech': 'Django', 'pos': (2, 0, 0), 'color': '#092e20'},
                {'name': 'Static Files', 'type': 'file_io', 'tech': 'CSS3', 'pos': (1, 2, 0), 'color': '#1572b6'},
            ]
            
        elif system.title == 'Task Management API':
            component_data = [
                {'name': 'REST API', 'type': 'api', 'tech': 'Django', 'pos': (0, 0, 0), 'color': '#092e20'},
                {'name': 'Authentication', 'type': 'authentication', 'tech': 'Django', 'pos': (-1, 1, 0), 'color': '#dc3545'},
                {'name': 'Database Layer', 'type': 'database', 'tech': 'PostgreSQL', 'pos': (0, -2, 0), 'color': '#336791'},
                {'name': 'API Documentation', 'type': 'other', 'tech': 'Python', 'pos': (2, 0, 0), 'color': '#17a2b8'},
            ]
            
        elif system.title == 'Environmental Data Analyzer':
            component_data = [
                {'name': 'Data Import', 'type': 'file_io', 'tech': 'Python', 'pos': (-2, 0, 0), 'color': '#3776ab'},
                {'name': 'Data Processing', 'type': 'processing', 'tech': 'Pandas', 'pos': (0, 0, 0), 'color': '#150458'},
                {'name': 'Visualization Engine', 'type': 'processing', 'tech': 'Matplotlib', 'pos': (0, 2, 0), 'color': '#11557c'},
                {'name': 'SQLite Storage', 'type': 'database', 'tech': 'SQLite', 'pos': (2, -1, 0), 'color': '#003b57'},
                {'name': 'Report Generator', 'type': 'file_io', 'tech': 'Python', 'pos': (2, 1, 0), 'color': '#3776ab'},
            ]
            
        else:
            # Generic components for other systems
            component_data = [
                {'name': 'Main Application', 'type': 'backend', 'tech': 'Python', 'pos': (0, 0, 0), 'color': '#3776ab'},
                {'name': 'User Interface', 'type': 'frontend', 'tech': 'HTML5', 'pos': (0, 1, 0), 'color': '#e34c26'},
                {'name': 'Data Storage', 'type': 'database', 'tech': 'SQLite', 'pos': (1, -1, 0), 'color': '#003b57'},
            ]
        
        # Create components
        system_components = []
        for comp_data in component_data:
            technology = next((t for t in technologies if t.name == comp_data['tech']), None)
            
            component, created = ArchitectureComponent.objects.get_or_create(
                system=system,
                name=comp_data['name'],
                defaults={
                    'component_type': comp_data['type'],
                    'position_x': comp_data['pos'][0],
                    'position_y': comp_data['pos'][1],
                    'position_z': comp_data['pos'][2],
                    'color': comp_data['color'],
                    'size': 18 if comp_data['type'] in ['backend', 'database'] else 15,
                    'technology': technology,
                    'description': f"{comp_data['name']} component for {system.title}",
                    'is_core': comp_data['type'] in ['backend', 'database'],
                    'display_order': len(system_components),
                }
            )
            system_components.append(component)
            components.append(component)
        
        # Create connections between components
        if len(system_components) >= 2:
            connection_pairs = []
            
            if system.title == 'AURA Portfolio System':
                connection_pairs = [
                    (0, 1, 'data_flow', 'Database Queries'),  # Backend -> Database
                    (0, 2, 'data_flow', 'Template Rendering'),  # Backend -> Frontend
                    (0, 3, 'data_flow', 'Admin Access'),  # Backend -> Admin
                    (2, 4, 'file_transfer', 'Static Assets'),  # Frontend -> Static
                ]
            elif system.title == 'Task Management API':
                connection_pairs = [
                    (0, 1, 'authentication', 'Auth Check'),  # API -> Auth
                    (0, 2, 'data_flow', 'Data Access'),  # API -> Database
                    (0, 3, 'api_call', 'Documentation'),  # API -> Docs
                ]
            else:
                # Generic connections
                for i in range(len(system_components) - 1):
                    connection_pairs.append((i, i+1, 'data_flow', f'Data Flow {i+1}'))
            
            for from_idx, to_idx, conn_type, label in connection_pairs:
                if from_idx < len(system_components) and to_idx < len(system_components):
                    connection, created = ArchitectureConnection.objects.get_or_create(
                        from_component=system_components[from_idx],
                        to_component=system_components[to_idx],
                        defaults={
                            'connection_type': conn_type,
                            'label': label,
                            'line_color': '#00ffff',
                            'line_width': 2,
                            'is_bidirectional': conn_type in ['data_flow', 'api_call'],
                        }
                    )
                    connections.append(connection)
    
    print(f"✅ Created {len(components)} architecture components and {len(connections)} connections")
    return components, connections

def create_system_dependencies(systems):
    """Create dependencies between systems"""
    print("🔗 Creating system dependencies...")
    
    dependencies = []
    
    # Portfolio system depends on others for content
    portfolio_system = next((s for s in systems if s.title == 'AURA Portfolio System'), None)
    if portfolio_system:
        for system in systems:
            if system != portfolio_system and system.status in ['published', 'deployed']:
                dependency, created = SystemDependency.objects.get_or_create(
                    system=portfolio_system,
                    depends_on=system,
                    defaults={
                        'dependency_type': 'data_flow',
                        'is_critical': False,
                        'description': f"Portfolio showcases {system.title} as a featured project.",
                    }
                )
                dependencies.append(dependency)
    
    print(f"✅ Created {len(dependencies)} system dependencies")
    return dependencies

def main():
    """Main execution function"""
    print("🚀 Starting Django Portfolio Data Population")
    print("=" * 50)
    
    # Optional: Clear existing data (uncomment if needed)
    # clear_all_data()
    
    try:
        # Create base data
        users = create_users()
        core_pages = create_core_pages()
        skills = create_skills()
        technologies = create_technologies()
        education_records = create_education(skills)
        experiences = create_experience()
        social_links = create_social_links()
        
        # Create project-related data
        system_types = create_system_types()
        categories, tags = create_categories_and_tags()
        systems = create_systems(system_types, technologies, skills)
        
        # Create blog content
        posts, series = create_blog_content(categories, tags, systems, users)
        comments, views = create_comments_and_views(posts, users)
        
        # Create additional data
        contacts = create_contacts()
        analytics = create_portfolio_analytics()
        skill_tech_relations = create_skill_technology_relations(skills, technologies)
        components, connections = create_architecture_components(systems, technologies)
        dependencies = create_system_dependencies(systems)
        
        print("\n" + "=" * 50)
        print("✅ DATA POPULATION COMPLETE!")
        print("=" * 50)
        
        # Summary
        print(f"📊 SUMMARY:")
        print(f"   Users: {len(users)}")
        print(f"   Skills: {len(skills)}")
        print(f"   Technologies: {len(technologies)}")
        print(f"   Systems: {len(systems)}")
        print(f"   Blog Posts: {len(posts)}")
        print(f"   Comments: {len(comments)}")
        print(f"   Page Views: {len(views)}")
        print(f"   Contacts: {len(contacts)}")
        print(f"   Analytics Records: {len(analytics)}")
        print(f"   Architecture Components: {len(components)}")
        print(f"   Architecture Connections: {len(connections)}")
        print(f"   System Dependencies: {len(dependencies)}")
        
        print("\n🎯 NEXT STEPS:")
        print("1. Visit /admin/ to review the populated data")
        print("2. Check the main site to see everything in action")
        print("3. Test search, filtering, and navigation features")
        print("4. Review system relationships and blog connections")
        
        print("\n📝 NOTE:")
        print("All sample data uses placeholder URLs and email addresses.")
        print("Update these with real information when deploying.")
        
    except Exception as e:
        print(f"\n❌ ERROR during data population: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()