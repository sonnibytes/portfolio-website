# projects/management/commands/populate_systems.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from projects.models import SystemModule, SystemType, Technology
from blog.models import Category, Post, SystemLogEntry
from django.utils import timezone
from django.utils.text import slugify
import random
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = "Populate the database with sample systems, technologies, and related data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing data before creating new data",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            self.stdout.write("🗑️  Clearing existing data...")
            SystemModule.objects.all().delete()
            SystemType.objects.all().delete()
            Technology.objects.all().delete()
            # Also clear core app skills that might be related
            try:
                from core.models import Skill

                Skill.objects.all().delete()
                self.stdout.write("   Cleared existing skills")
            except ImportError:
                pass

        self.stdout.write("🚀 Creating sample portfolio data...")

        # Create user if needed
        user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            user.set_password("admin")
            user.save()

        # Create Core App Skills (if available)
        self.create_core_skills()

        # Create Technologies
        self.create_technologies()

        # Create System Types
        self.create_system_types()

        # Create Systems
        self.create_systems(user)

        # Create some DataLog entries if blog app exists
        self.create_sample_logs(user)

        self.stdout.write(
            self.style.SUCCESS("✅ Successfully created sample portfolio data!")
        )
        self.stdout.write("📊 Summary:")
        self.stdout.write(f"   • {SystemModule.objects.count()} Systems")
        self.stdout.write(f"   • {Technology.objects.count()} Technologies")
        self.stdout.write(f"   • {SystemType.objects.count()} System Types")

        # Show core app integration if available
        try:
            from core.models import Skill

            self.stdout.write(f"   • {Skill.objects.count()} Skills (Core App)")
        except ImportError:
            pass

    def create_core_skills(self):
        """Create skills in the core app that complement our technologies"""
        try:
            from core.models import Skill

            skills_data = [
                # Programming Languages
                {
                    "name": "Python",
                    "category": "languages",
                    "proficiency": 5,
                    "icon": "fab fa-python",
                    "color": "#3776ab",
                },
                {
                    "name": "JavaScript",
                    "category": "languages",
                    "proficiency": 4,
                    "icon": "fab fa-js-square",
                    "color": "#f7df1e",
                },
                {
                    "name": "TypeScript",
                    "category": "languages",
                    "proficiency": 4,
                    "icon": "fab fa-js-square",
                    "color": "#3178c6",
                },
                {
                    "name": "SQL",
                    "category": "languages",
                    "proficiency": 4,
                    "icon": "fas fa-database",
                    "color": "#336791",
                },
                {
                    "name": "HTML/CSS",
                    "category": "languages",
                    "proficiency": 5,
                    "icon": "fab fa-html5",
                    "color": "#e34f26",
                },
                # Frameworks & Libraries
                {
                    "name": "Django",
                    "category": "frameworks",
                    "proficiency": 5,
                    "icon": "fab fa-python",
                    "color": "#092e20",
                },
                {
                    "name": "Flask",
                    "category": "frameworks",
                    "proficiency": 4,
                    "icon": "fab fa-python",
                    "color": "#000000",
                },
                {
                    "name": "FastAPI",
                    "category": "frameworks",
                    "proficiency": 4,
                    "icon": "fas fa-bolt",
                    "color": "#009688",
                },
                {
                    "name": "React",
                    "category": "frameworks",
                    "proficiency": 4,
                    "icon": "fab fa-react",
                    "color": "#61dafb",
                },
                {
                    "name": "Vue.js",
                    "category": "frameworks",
                    "proficiency": 3,
                    "icon": "fab fa-vuejs",
                    "color": "#4fc08d",
                },
                {
                    "name": "Pandas",
                    "category": "frameworks",
                    "proficiency": 4,
                    "icon": "fas fa-chart-bar",
                    "color": "#150458",
                },
                {
                    "name": "Scikit-learn",
                    "category": "frameworks",
                    "proficiency": 3,
                    "icon": "fas fa-brain",
                    "color": "#f7931e",
                },
                # Databases
                {
                    "name": "PostgreSQL",
                    "category": "databases",
                    "proficiency": 4,
                    "icon": "fas fa-database",
                    "color": "#336791",
                },
                {
                    "name": "Redis",
                    "category": "databases",
                    "proficiency": 3,
                    "icon": "fas fa-memory",
                    "color": "#dc382d",
                },
                {
                    "name": "MongoDB",
                    "category": "databases",
                    "proficiency": 3,
                    "icon": "fas fa-leaf",
                    "color": "#47a248",
                },
                # Tools & Technologies
                {
                    "name": "Git",
                    "category": "tools",
                    "proficiency": 5,
                    "icon": "fab fa-git-alt",
                    "color": "#f05032",
                },
                {
                    "name": "Docker",
                    "category": "tools",
                    "proficiency": 4,
                    "icon": "fab fa-docker",
                    "color": "#2496ed",
                },
                {
                    "name": "AWS",
                    "category": "tools",
                    "proficiency": 3,
                    "icon": "fab fa-aws",
                    "color": "#ff9900",
                },
                {
                    "name": "Kubernetes",
                    "category": "tools",
                    "proficiency": 3,
                    "icon": "fas fa-dharmachakra",
                    "color": "#326ce5",
                },
                {
                    "name": "Linux",
                    "category": "tools",
                    "proficiency": 4,
                    "icon": "fab fa-linux",
                    "color": "#fcc624",
                },
                {
                    "name": "Nginx",
                    "category": "tools",
                    "proficiency": 3,
                    "icon": "fas fa-server",
                    "color": "#009639",
                },
                # Other Skills
                {
                    "name": "API Design",
                    "category": "other",
                    "proficiency": 5,
                    "icon": "fas fa-plug",
                    "color": "#26c6da",
                },
                {
                    "name": "Database Design",
                    "category": "other",
                    "proficiency": 4,
                    "icon": "fas fa-sitemap",
                    "color": "#ff8a80",
                },
                {
                    "name": "System Architecture",
                    "category": "other",
                    "proficiency": 4,
                    "icon": "fas fa-project-diagram",
                    "color": "#b39ddb",
                },
                {
                    "name": "DevOps",
                    "category": "other",
                    "proficiency": 3,
                    "icon": "fas fa-cogs",
                    "color": "#a5d6a7",
                },
                {
                    "name": "Machine Learning",
                    "category": "other",
                    "proficiency": 3,
                    "icon": "fas fa-brain",
                    "color": "#fff59d",
                },
            ]

            for i, skill_data in enumerate(skills_data):
                skill, created = Skill.objects.get_or_create(
                    name=skill_data["name"],
                    defaults={
                        "category": skill_data["category"],
                        "proficiency": skill_data["proficiency"],
                        "icon": skill_data["icon"],
                        "color": skill_data["color"],
                        "display_order": i,
                        "description": f"Professional experience with {skill_data['name']}",
                    },
                )
                if created:
                    self.stdout.write(f"   Created skill: {skill.name}")

        except ImportError:
            self.stdout.write(
                "   Skipping Skills creation (core app models not available)"
            )

    def create_technologies(self):
        """Create realistic technologies for a Python developer portfolio"""
        technologies_data = [
            # Programming Languages
            {
                "name": "Python",
                "category": "language",
                "color": "#3776ab",
                "description": "Primary programming language",
            },
            {
                "name": "JavaScript",
                "category": "language",
                "color": "#f7df1e",
                "description": "Frontend and full-stack development",
            },
            {
                "name": "TypeScript",
                "category": "language",
                "color": "#3178c6",
                "description": "Type-safe JavaScript development",
            },
            {
                "name": "SQL",
                "category": "language",
                "color": "#336791",
                "description": "Database query language",
            },
            # Web Frameworks
            {
                "name": "Django",
                "category": "framework",
                "color": "#092e20",
                "description": "Python web framework",
            },
            {
                "name": "Flask",
                "category": "framework",
                "color": "#000000",
                "description": "Lightweight Python web framework",
            },
            {
                "name": "FastAPI",
                "category": "framework",
                "color": "#009688",
                "description": "Modern Python API framework",
            },
            {
                "name": "React",
                "category": "framework",
                "color": "#61dafb",
                "description": "Frontend JavaScript library",
            },
            {
                "name": "Vue.js",
                "category": "framework",
                "color": "#4fc08d",
                "description": "Progressive JavaScript framework",
            },
            # Databases
            {
                "name": "PostgreSQL",
                "category": "database",
                "color": "#336791",
                "description": "Advanced relational database",
            },
            {
                "name": "Redis",
                "category": "database",
                "color": "#dc382d",
                "description": "In-memory data structure store",
            },
            {
                "name": "MongoDB",
                "category": "database",
                "color": "#47a248",
                "description": "NoSQL document database",
            },
            # Cloud & DevOps
            {
                "name": "AWS",
                "category": "cloud",
                "color": "#ff9900",
                "description": "Amazon Web Services",
            },
            {
                "name": "Docker",
                "category": "tool",
                "color": "#2496ed",
                "description": "Containerization platform",
            },
            {
                "name": "Kubernetes",
                "category": "tool",
                "color": "#326ce5",
                "description": "Container orchestration",
            },
            {
                "name": "GitHub Actions",
                "category": "tool",
                "color": "#2088ff",
                "description": "CI/CD automation",
            },
            # Data & AI
            {
                "name": "Pandas",
                "category": "framework",
                "color": "#150458",
                "description": "Data manipulation library",
            },
            {
                "name": "Scikit-learn",
                "category": "framework",
                "color": "#f7931e",
                "description": "Machine learning library",
            },
            {
                "name": "TensorFlow",
                "category": "framework",
                "color": "#ff6f00",
                "description": "Machine learning framework",
            },
            # Tools
            {
                "name": "Git",
                "category": "tool",
                "color": "#f05032",
                "description": "Version control system",
            },
            {
                "name": "Celery",
                "category": "tool",
                "color": "#37b24d",
                "description": "Distributed task queue",
            },
            {
                "name": "Nginx",
                "category": "tool",
                "color": "#009639",
                "description": "Web server and reverse proxy",
            },
        ]

        for tech_data in technologies_data:
            tech, created = Technology.objects.get_or_create(
                name=tech_data["name"],
                defaults={
                    "slug": slugify(tech_data["name"]),
                    "category": tech_data["category"],
                    "color": tech_data["color"],
                    "description": tech_data.get("description", ""),
                    "is_primary_skill": tech_data["name"]
                    in ["Python", "Django", "PostgreSQL", "React", "AWS"],
                },
            )
            if created:
                self.stdout.write(f"   Created technology: {tech.name}")

    def create_system_types(self):
        """Create system types for portfolio"""
        system_types_data = [
            {
                "name": "Web Application",
                "description": "Full-stack web applications with user interfaces",
                "icon": "fas fa-globe",
                "color": "#26c6da",
            },
            {
                "name": "API Service",
                "description": "REST APIs and backend services",
                "icon": "fas fa-server",
                "color": "#ff8a80",
            },
            {
                "name": "Data Pipeline",
                "description": "Data processing and ETL systems",
                "icon": "fas fa-stream",
                "color": "#a5d6a7",
            },
            {
                "name": "Machine Learning",
                "description": "ML models and AI applications",
                "icon": "fas fa-brain",
                "color": "#b39ddb",
            },
            {
                "name": "DevOps Tool",
                "description": "Automation and infrastructure tools",
                "icon": "fas fa-cogs",
                "color": "#fff59d",
            },
            {
                "name": "Mobile App",
                "description": "Mobile applications and responsive web apps",
                "icon": "fas fa-mobile-alt",
                "color": "#ffab91",
            },
        ]

        for type_data in system_types_data:
            system_type, created = SystemType.objects.get_or_create(
                name=type_data["name"],
                defaults={
                    "slug": slugify(type_data["name"]),
                    "description": type_data["description"],
                    "icon": type_data["icon"],
                    "color": type_data["color"],
                },
            )
            if created:
                self.stdout.write(f"   Created system type: {system_type.name}")

    def create_systems(self, user):
        """Create realistic portfolio systems"""
        systems_data = [
            {
                "title": "AURA Portfolio System",
                "subtitle": "Advanced User Repository & Archive",
                "description": """
A sophisticated Django-based portfolio system featuring a HUD-inspired design and real-time analytics. 
Built with modern web technologies and deployment best practices.

## Key Features
- **Real-time Dashboard**: Live system metrics and analytics
- **HUD Interface**: Futuristic design with glass-morphism effects  
- **Content Management**: Advanced blog and project management
- **Performance Monitoring**: System uptime and performance tracking
- **Responsive Design**: Mobile-first approach with progressive enhancement

## Technical Implementation
The system uses Django's class-based views for maintainable code, PostgreSQL for robust data storage, 
and Redis for caching and session management. The frontend leverages modern CSS techniques and 
progressive JavaScript enhancement.
                """,
                "system_type": "Web Application",
                "status": "deployed",
                "completion_percent": 95,
                "complexity": 4,
                "priority": 4,
                "featured": True,
                "github_url": "https://github.com/username/aura-portfolio",
                "live_url": "https://portfolio.example.com",
                "technologies": [
                    "Python",
                    "Django",
                    "PostgreSQL",
                    "Redis",
                    "JavaScript",
                    "AWS",
                ],
                "uptime_percentage": 99.8,
                "performance_score": 92.5,
            },
            {
                "title": "TaskFlow API",
                "subtitle": "Distributed Task Management Service",
                "description": """
A high-performance REST API for task management with real-time notifications and team collaboration features.
Designed for scalability and built with FastAPI for maximum performance.

## Core Capabilities
- **Task Management**: Create, assign, and track tasks with dependencies
- **Real-time Updates**: WebSocket connections for live collaboration
- **Team Management**: Role-based access control and permissions
- **Integration Ready**: RESTful API with comprehensive documentation

## Architecture
Microservices architecture with FastAPI, Celery for background tasks, and Redis for real-time messaging.
Deployed on Kubernetes for high availability and auto-scaling.
                """,
                "system_type": "API Service",
                "status": "deployed",
                "completion_percent": 88,
                "complexity": 4,
                "priority": 3,
                "featured": True,
                "github_url": "https://github.com/username/taskflow-api",
                "live_url": "https://api.taskflow.example.com",
                "documentation_url": "https://docs.taskflow.example.com",
                "technologies": [
                    "Python",
                    "FastAPI",
                    "PostgreSQL",
                    "Redis",
                    "Celery",
                    "Kubernetes",
                ],
                "uptime_percentage": 99.5,
                "performance_score": 95.2,
            },
            {
                "title": "DataViz Analytics Platform",
                "subtitle": "Interactive Data Visualization Dashboard",
                "description": """
A comprehensive analytics platform for visualizing complex datasets with interactive charts and real-time updates.
Built with React frontend and Python backend for optimal performance.

## Features
- **Interactive Charts**: D3.js-powered visualizations with zoom and pan
- **Real-time Data**: Live updates via WebSocket connections
- **Custom Dashboards**: Drag-and-drop dashboard builder
- **Data Sources**: Connect to multiple databases and APIs
- **Export Options**: PDF, PNG, and CSV export capabilities

## Technology Stack
React with TypeScript for the frontend, Django REST Framework for the API, and Pandas for data processing.
Containerized with Docker and deployed on AWS with auto-scaling.
                """,
                "system_type": "Web Application",
                "status": "in_development",
                "completion_percent": 72,
                "complexity": 5,
                "priority": 3,
                "featured": True,
                "github_url": "https://github.com/username/dataviz-platform",
                "technologies": [
                    "Python",
                    "Django",
                    "React",
                    "TypeScript",
                    "Pandas",
                    "AWS",
                    "Docker",
                ],
                "uptime_percentage": 95.2,
                "performance_score": 87.8,
            },
            {
                "title": "ML Model Pipeline",
                "subtitle": "Automated Machine Learning Workflow",
                "description": """
An end-to-end machine learning pipeline for automated model training, validation, and deployment.
Supports multiple ML frameworks and provides model versioning and monitoring.

## Capabilities
- **Auto-Training**: Scheduled model retraining with new data
- **Model Versioning**: Track model performance over time
- **A/B Testing**: Compare model versions in production
- **Performance Monitoring**: Real-time model drift detection

Built with MLflow for experiment tracking and deployed using Kubernetes for scalability.
                """,
                "system_type": "Machine Learning",
                "status": "testing",
                "completion_percent": 65,
                "complexity": 5,
                "priority": 2,
                "featured": False,
                "github_url": "https://github.com/username/ml-pipeline",
                "technologies": [
                    "Python",
                    "Scikit-learn",
                    "TensorFlow",
                    "Docker",
                    "Kubernetes",
                ],
                "uptime_percentage": 92.1,
                "performance_score": 89.3,
            },
            {
                "title": "DevOps Automation Suite",
                "subtitle": "Infrastructure as Code Management",
                "description": """
A comprehensive DevOps toolkit for automating infrastructure deployment and management.
Includes CI/CD pipelines, monitoring, and automated scaling capabilities.

## Tools Included
- **Infrastructure Automation**: Terraform and Ansible integration
- **CI/CD Pipelines**: GitHub Actions workflows
- **Monitoring Stack**: Prometheus and Grafana dashboards
- **Log Aggregation**: ELK stack for centralized logging

Designed for cloud-native applications with support for multi-cloud deployments.
                """,
                "system_type": "DevOps Tool",
                "status": "deployed",
                "completion_percent": 82,
                "complexity": 3,
                "priority": 2,
                "featured": False,
                "github_url": "https://github.com/username/devops-suite",
                "technologies": [
                    "Python",
                    "Docker",
                    "Kubernetes",
                    "GitHub Actions",
                    "AWS",
                ],
                "uptime_percentage": 98.7,
                "performance_score": 91.4,
            },
            {
                "title": "E-Commerce Analytics",
                "subtitle": "Real-time Sales Dashboard",
                "description": """
A real-time analytics dashboard for e-commerce platforms with sales tracking, customer insights, 
and inventory management features.

## Features
- **Sales Analytics**: Real-time revenue and conversion tracking
- **Customer Insights**: Behavior analysis and segmentation
- **Inventory Management**: Stock level monitoring and alerts
- **Predictive Analytics**: Sales forecasting and trend analysis

Built with Vue.js frontend and Django backend, optimized for high-traffic e-commerce sites.
                """,
                "system_type": "Web Application",
                "status": "draft",
                "completion_percent": 35,
                "complexity": 3,
                "priority": 1,
                "featured": False,
                "github_url": "https://github.com/username/ecommerce-analytics",
                "technologies": ["Python", "Django", "Vue.js", "PostgreSQL", "Redis"],
                "uptime_percentage": None,
                "performance_score": None,
            },
        ]

        for system_data in systems_data:
            # Get system type
            system_type = SystemType.objects.get(name=system_data["system_type"])

            # Create system
            system, created = SystemModule.objects.get_or_create(
                title=system_data["title"],
                defaults={
                    "slug": slugify(system_data["title"]),
                    "subtitle": system_data["subtitle"],
                    "description": system_data["description"],
                    "excerpt": system_data["description"][:200] + "...",
                    "system_type": system_type,
                    "author": user,
                    "status": system_data["status"],
                    "completion_percent": system_data["completion_percent"],
                    "complexity": system_data["complexity"],
                    "priority": system_data["priority"],
                    "featured": system_data["featured"],
                    "github_url": system_data.get("github_url", ""),
                    "live_url": system_data.get("live_url", ""),
                    "documentation_url": system_data.get("documentation_url", ""),
                    "uptime_percentage": system_data.get("uptime_percentage"),
                    "performance_score": system_data.get("performance_score"),
                    "start_date": timezone.now().date()
                    - timedelta(days=random.randint(30, 300)),
                    "end_date": timezone.now().date()
                    - timedelta(days=random.randint(0, 30))
                    if system_data["status"] in ["deployed"]
                    else None,
                    "deployment_date": timezone.now().date()
                    - timedelta(days=random.randint(0, 30))
                    if system_data["status"] == "deployed"
                    else None,
                },
            )

            if created:
                # Add technologies
                for tech_name in system_data["technologies"]:
                    try:
                        tech = Technology.objects.get(name=tech_name)
                        system.technologies.add(tech)
                    except Technology.DoesNotExist:
                        pass

                self.stdout.write(f"   Created system: {system.title}")

    def create_sample_logs(self, user):
        """Create sample DataLog entries connected to systems"""
        try:
            from blog.models import Category, Post, SystemLogEntry

            # Create a category for system logs
            category, created = Category.objects.get_or_create(
                name="System Development",
                defaults={
                    "slug": "system-development",
                    "code": "SYS",
                    "description": "Development logs and technical documentation",
                    "color": "#26c6da",
                },
            )

            # Create some sample posts
            systems = SystemModule.objects.all()[:3]  # First 3 systems

            log_posts_data = [
                {
                    "title": "AURA Portfolio - Development Kickoff",
                    "content": """
# Project Initialization

Started development of the AURA portfolio system with focus on:

- Modern Django architecture
- HUD-inspired design system
- Real-time analytics integration
- Performance optimization

## Technical Decisions

- **Backend**: Django with class-based views
- **Database**: PostgreSQL for reliability
- **Frontend**: Progressive enhancement with vanilla JS
- **Deployment**: AWS with Docker containers

The foundation is solid and ready for iterative development.
                    """,
                    "system": systems[0] if systems else None,
                    "connection_type": "development",
                },
                {
                    "title": "API Performance Optimization Results",
                    "content": """
# TaskFlow API Optimization

Completed performance optimization phase with impressive results:

## Improvements Achieved

- **Response Time**: Reduced from 250ms to 85ms (66% improvement)
- **Throughput**: Increased from 1000 to 3500 requests/second
- **Memory Usage**: Optimized to use 40% less RAM
- **Database Queries**: Reduced N+1 queries by 95%

## Key Optimizations

1. Database index optimization
2. Query result caching with Redis
3. API response compression
4. Connection pooling improvements

Ready for production deployment with confidence.
                    """,
                    "system": systems[1] if len(systems) > 1 else None,
                    "connection_type": "analysis",
                },
                {
                    "title": "DataViz Platform - Technical Architecture",
                    "content": """
# Architecture Documentation

Designing the DataViz Analytics Platform with scalability in mind:

## System Components

- **Frontend**: React with TypeScript for type safety
- **API Layer**: Django REST Framework with custom permissions
- **Data Processing**: Pandas and NumPy for heavy computations
- **Real-time**: WebSocket connections for live updates
- **Storage**: PostgreSQL + Redis for optimal performance

## Challenges & Solutions

The main challenge is handling large datasets efficiently. Solution includes:
- Chunked data processing
- Progressive loading strategies
- Client-side caching mechanisms

Development is progressing well with 72% completion.
                    """,
                    "system": systems[2] if len(systems) > 2 else None,
                    "connection_type": "documentation",
                },
            ]

            for i, log_data in enumerate(log_posts_data):
                if log_data["system"]:
                    post, created = Post.objects.get_or_create(
                        title=log_data["title"],
                        defaults={
                            "slug": slugify(log_data["title"]),
                            "content": log_data["content"],
                            "excerpt": log_data["content"][:200] + "...",
                            "author": user,
                            "category": category,
                            "status": "published",
                            "published_date": timezone.now()
                            - timedelta(days=random.randint(1, 30)),
                            "reading_time": 3,
                        },
                    )

                    if created:
                        # Create system log entry connection
                        SystemLogEntry.objects.create(
                            post=post,
                            system=log_data["system"],
                            connection_type=log_data["connection_type"],
                            priority=random.randint(1, 4),
                            log_entry_id=f"SYS-{log_data['system'].id:03d}-LOG-{i + 1:03d}",
                            created_at=post.published_date,
                        )

                        self.stdout.write(f"   Created log entry: {post.title}")

        except ImportError:
            self.stdout.write("   Skipping DataLog creation (blog app not available)")
