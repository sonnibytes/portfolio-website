from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from datetime import timedelta, date
import random
from decimal import Decimal

# Import all our enhanced models
from projects.models import (
    SystemModule,
    SystemType,
    Technology,
    SystemFeature,
    SystemImage,
    SystemMetric,
    SystemDependency,
)
from blog.models import Category, Post, SystemLogEntry, Series
from core.models import Skill, PortfolioAnalytics, Contact

User = get_user_model()


class Command(BaseCommand):
    help = "Populate the database with comprehensive sample data for enhanced AURA portfolio"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing data before creating new data",
        )
        parser.add_argument(
            "--minimal",
            action="store_true",
            help="Create minimal dataset for testing",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            self.stdout.write("🗑️  Clearing existing data...")
            self._clear_existing_data()

        self.stdout.write("🚀 Creating enhanced portfolio data...")

        # Better user handling - don't create admin users
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            self.stdout.write(
                "❌ No superuser found. Please create one with: python manage.py createsuperuser"
            )
            return

        # Create data based on options
        if options["minimal"]:
            self._create_minimal_dataset(user)
        else:
            self._create_comprehensive_dataset(user)

        self._display_summary()

    def _clear_existing_data(self):
        """Clear existing sample data"""
        models_to_clear = [
            SystemLogEntry,
            SystemDependency,
            SystemMetric,
            SystemFeature,
            SystemImage,
            SystemModule,
            SystemType,
            Technology,
            Post,
            Category,
            Series,
            Skill,
            PortfolioAnalytics,
            Contact,
        ]

        for model in models_to_clear:
            try:
                count = model.objects.count()
                model.objects.all().delete()
                self.stdout.write(f"   Cleared {count} {model.__name__} records")
            except Exception as e:
                self.stdout.write(f"   Warning: Could not clear {model.__name__}: {e}")

    def _create_minimal_dataset(self, user):
        """Create minimal dataset for testing"""
        self.stdout.write("📝 Creating minimal dataset...")
        self._create_technologies(5)
        self._create_system_types(3)
        self._create_systems(user, 3)
        self._create_blog_data(user, minimal=True)
        self._create_core_skills(10)

    def _create_comprehensive_dataset(self, user):
        """Create comprehensive realistic dataset"""
        self.stdout.write("📊 Creating comprehensive dataset...")
        self._create_technologies()
        self._create_system_types()
        self._create_systems(user)
        self._create_system_features()
        self._create_system_metrics()
        self._create_system_dependencies()
        self._create_blog_data(user)
        self._create_core_skills()
        self._create_portfolio_analytics()
        self._create_sample_contacts()

    def _create_technologies(self, limit=None):
        """Create realistic technologies with enhanced fields"""
        technologies_data = [
            # Programming Languages
            {
                "name": "Python",
                "category": "language",
                "color": "#3776ab",
                "icon": "fab fa-python",
            },
            {
                "name": "JavaScript",
                "category": "language",
                "color": "#f7df1e",
                "icon": "fab fa-js-square",
            },
            {
                "name": "TypeScript",
                "category": "language",
                "color": "#3178c6",
                "icon": "fab fa-js-square",
            },
            {
                "name": "SQL",
                "category": "language",
                "color": "#336791",
                "icon": "fas fa-database",
            },
            # Web Frameworks
            {
                "name": "Django",
                "category": "framework",
                "color": "#092e20",
                "icon": "fab fa-python",
            },
            {
                "name": "Flask",
                "category": "framework",
                "color": "#000000",
                "icon": "fab fa-python",
            },
            {
                "name": "FastAPI",
                "category": "framework",
                "color": "#009688",
                "icon": "fas fa-bolt",
            },
            {
                "name": "React",
                "category": "framework",
                "color": "#61dafb",
                "icon": "fab fa-react",
            },
            {
                "name": "Vue.js",
                "category": "framework",
                "color": "#4fc08d",
                "icon": "fab fa-vuejs",
            },
            # Databases
            {
                "name": "PostgreSQL",
                "category": "database",
                "color": "#336791",
                "icon": "fas fa-database",
            },
            {
                "name": "Redis",
                "category": "database",
                "color": "#dc382d",
                "icon": "fas fa-memory",
            },
            {
                "name": "MongoDB",
                "category": "database",
                "color": "#47a248",
                "icon": "fas fa-leaf",
            },
            # Cloud & DevOps
            {
                "name": "AWS",
                "category": "cloud",
                "color": "#ff9900",
                "icon": "fab fa-aws",
            },
            {
                "name": "Docker",
                "category": "tool",
                "color": "#2496ed",
                "icon": "fab fa-docker",
            },
            {
                "name": "Kubernetes",
                "category": "tool",
                "color": "#326ce5",
                "icon": "fas fa-dharmachakra",
            },
            {
                "name": "GitHub Actions",
                "category": "tool",
                "color": "#2088ff",
                "icon": "fab fa-github",
            },
            # Data & AI
            {
                "name": "Pandas",
                "category": "framework",
                "color": "#150458",
                "icon": "fas fa-chart-bar",
            },
            {
                "name": "Scikit-learn",
                "category": "framework",
                "color": "#f7931e",
                "icon": "fas fa-brain",
            },
            {
                "name": "TensorFlow",
                "category": "framework",
                "color": "#ff6f00",
                "icon": "fas fa-brain",
            },
            # Tools
            {
                "name": "Git",
                "category": "tool",
                "color": "#f05032",
                "icon": "fab fa-git-alt",
            },
            {
                "name": "Celery",
                "category": "tool",
                "color": "#37b24d",
                "icon": "fas fa-tasks",
            },
            {
                "name": "Nginx",
                "category": "tool",
                "color": "#009639",
                "icon": "fas fa-server",
            },
        ]

        if limit:
            technologies_data = technologies_data[:limit]

        for tech_data in technologies_data:
            tech, created = Technology.objects.get_or_create(
                name=tech_data["name"],
                defaults={
                    "slug": slugify(tech_data["name"]),
                    "category": tech_data["category"],
                    "color": tech_data["color"],
                    "icon": tech_data.get("icon", ""),
                    "description": f"Professional experience with {tech_data['name']}",
                },
            )
            if created:
                self.stdout.write(f"   ✅ Created technology: {tech.name}")

    def _create_system_types(self, limit=None):
        """Create system types with enhanced display properties"""
        system_types_data = [
            {
                "name": "Web Application",
                "code": "WEB",
                "color": "#00f0ff",
                "icon": "fas fa-globe",
            },
            {
                "name": "API Service",
                "code": "API",
                "color": "#ff8a80",
                "icon": "fas fa-plug",
            },
            {
                "name": "Machine Learning",
                "code": "ML",
                "color": "#b39ddb",
                "icon": "fas fa-brain",
            },
            {
                "name": "DevOps Tool",
                "code": "OPS",
                "color": "#a5d6a7",
                "icon": "fas fa-cogs",
            },
            {
                "name": "Data Pipeline",
                "code": "DATA",
                "color": "#fff59d",
                "icon": "fas fa-database",
            },
            {
                "name": "Mobile App",
                "code": "MOB",
                "color": "#ffcc02",
                "icon": "fas fa-mobile-alt",
            },
        ]

        if limit:
            system_types_data = system_types_data[:limit]

        for i, sys_type_data in enumerate(system_types_data):
            sys_type, created = SystemType.objects.get_or_create(
                name=sys_type_data["name"],
                defaults={
                    "slug": slugify(sys_type_data["name"]),
                    "code": sys_type_data["code"],
                    "color": sys_type_data["color"],
                    "icon": sys_type_data["icon"],
                    "description": f"Systems focused on {sys_type_data['name'].lower()}",
                    "display_order": i,
                },
            )
            if created:
                self.stdout.write(f"   ✅ Created system type: {sys_type.name}")

    def _create_systems(self, user, limit=None):
        """Create realistic systems with all enhanced fields"""
        systems_data = [
            {
                "title": "AURA Portfolio Platform",
                "subtitle": "Advanced Django Portfolio with HUD Theme",
                "description": """
A sophisticated portfolio platform built with Django, featuring a cyberpunk HUD-style interface 
and comprehensive project management capabilities.

## Key Features
- **Modern Design**: Cyberpunk-inspired HUD interface with smooth animations
- **Blog System**: Technical blog with syntax highlighting and series organization
- **Project Showcase**: Detailed system documentation with metrics and analytics
- **Real-time Metrics**: Live performance monitoring and analytics dashboard
- **Responsive Design**: Mobile-first approach with progressive enhancement

Built using Django 4.2, PostgreSQL, Redis for caching, and deployed on AWS with CI/CD automation.
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
                "performance_score": Decimal("92.5"),
                "uptime_percentage": Decimal("99.8"),
                "response_time_ms": 180,
                "daily_users": 245,
                "team_size": 1,
                "estimated_dev_hours": 120,
                "actual_dev_hours": 145,
                "code_lines": 8500,
                "commit_count": 156,
            },
            {
                "title": "TaskFlow API",
                "subtitle": "Distributed Task Management Service",
                "description": """
High-performance REST API for task management with real-time notifications and team collaboration.
Built with FastAPI for maximum performance and scalability.

## Core Capabilities
- **Task Management**: Create, assign, and track tasks with dependencies
- **Real-time Updates**: WebSocket connections for live collaboration
- **Team Management**: Role-based access control and permissions
- **API Integration**: RESTful API with comprehensive OpenAPI documentation

Architecture: Microservices with FastAPI, Celery background tasks, Redis messaging, 
and Kubernetes deployment for high availability.
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
                "performance_score": Decimal("95.2"),
                "uptime_percentage": Decimal("99.5"),
                "response_time_ms": 85,
                "daily_users": 1250,
                "team_size": 3,
                "estimated_dev_hours": 200,
                "actual_dev_hours": 180,
                "code_lines": 12000,
                "commit_count": 289,
            },
            {
                "title": "DataViz Analytics Platform",
                "subtitle": "Interactive Data Visualization Dashboard",
                "description": """
Comprehensive analytics platform for visualizing complex datasets with interactive charts 
and real-time updates. Built for enterprise-level data analysis.

## Features
- **Interactive Charts**: D3.js-powered visualizations with zoom and pan
- **Real-time Data**: Live updates via WebSocket connections
- **Custom Dashboards**: Drag-and-drop dashboard builder
- **Data Sources**: Multiple database and API connections
- **Export Options**: PDF, PNG, and CSV export capabilities

Technology Stack: React with TypeScript frontend, Django REST API, 
Pandas for data processing, containerized with Docker.
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
                "performance_score": Decimal("87.8"),
                "uptime_percentage": Decimal("95.2"),
                "response_time_ms": 320,
                "daily_users": 580,
                "team_size": 4,
                "estimated_dev_hours": 300,
                "actual_dev_hours": 220,
                "code_lines": 15000,
                "commit_count": 198,
            },
            {
                "title": "ML Model Pipeline",
                "subtitle": "Automated Machine Learning Workflow",
                "description": """
End-to-end machine learning pipeline for automated model training, validation, and deployment.
Supports multiple ML frameworks with comprehensive monitoring.

## Capabilities
- **Auto-Training**: Scheduled model retraining with new data
- **Model Versioning**: Track performance over time with MLflow
- **A/B Testing**: Compare model versions in production
- **Drift Detection**: Real-time model performance monitoring

Built with MLflow for experiment tracking, deployed using Kubernetes 
for scalability and high availability.
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
                "performance_score": Decimal("89.3"),
                "uptime_percentage": Decimal("92.1"),
                "response_time_ms": 1200,
                "daily_users": 45,
                "team_size": 2,
                "estimated_dev_hours": 180,
                "actual_dev_hours": 165,
                "code_lines": 9500,
                "commit_count": 134,
            },
            {
                "title": "DevOps Automation Suite",
                "subtitle": "Infrastructure as Code Management",
                "description": """
Comprehensive DevOps toolkit for automating infrastructure deployment and management.
Includes CI/CD pipelines, monitoring, and automated scaling.

## Tools Included
- **Infrastructure Automation**: Terraform and Ansible integration
- **CI/CD Pipelines**: GitHub Actions workflows
- **Monitoring Stack**: Prometheus and Grafana dashboards
- **Log Aggregation**: ELK stack for centralized logging

Designed for cloud-native applications with multi-cloud deployment support.
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
                "performance_score": Decimal("91.4"),
                "uptime_percentage": Decimal("98.7"),
                "response_time_ms": 450,
                "daily_users": 120,
                "team_size": 2,
                "estimated_dev_hours": 100,
                "actual_dev_hours": 95,
                "code_lines": 6800,
                "commit_count": 87,
            },
            {
                "title": "E-Commerce Analytics",
                "subtitle": "Real-time Sales Dashboard",
                "description": """
Real-time analytics dashboard for e-commerce platforms with sales tracking, 
customer insights, and inventory management.

## Features
- **Sales Analytics**: Real-time revenue and conversion tracking
- **Customer Insights**: Behavior analysis and segmentation
- **Inventory Management**: Stock level monitoring and alerts
- **Predictive Analytics**: Sales forecasting and trend analysis

Built with Vue.js frontend and Django backend, optimized for high-traffic sites.
                """,
                "system_type": "Web Application",
                "status": "draft",
                "completion_percent": 35,
                "complexity": 3,
                "priority": 1,
                "featured": False,
                "github_url": "https://github.com/username/ecommerce-analytics",
                "technologies": ["Python", "Django", "Vue.js", "PostgreSQL", "Redis"],
                "performance_score": None,
                "uptime_percentage": None,
                "response_time_ms": 0,
                "daily_users": 0,
                "team_size": 1,
                "estimated_dev_hours": 150,
                "actual_dev_hours": 48,
                "code_lines": 2800,
                "commit_count": 42,
            },
        ]

        if limit:
            systems_data = systems_data[:limit]

        created_systems = []
        for system_data in systems_data:
            # Get system type
            system_type = SystemType.objects.get(name=system_data["system_type"])

            # Create system with all enhanced fields
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
                    "github_url": system_data["github_url"],
                    "live_url": system_data.get("live_url", ""),
                    "documentation_url": system_data.get("documentation_url", ""),
                    # Enhanced performance fields
                    "performance_score": system_data.get("performance_score"),
                    "uptime_percentage": system_data.get("uptime_percentage"),
                    "response_time_ms": system_data.get("response_time_ms", 0),
                    "daily_users": system_data.get("daily_users", 0),
                    # Development tracking fields
                    "team_size": system_data.get("team_size", 1),
                    "estimated_dev_hours": system_data.get("estimated_dev_hours"),
                    "actual_dev_hours": system_data.get("actual_dev_hours"),
                    "code_lines": system_data.get("code_lines", 0),
                    "commit_count": system_data.get("commit_count", 0),
                    "last_commit_date": timezone.now()
                    - timedelta(days=random.randint(1, 30)),
                    # Timeline fields
                    "start_date": timezone.now().date()
                    - timedelta(days=random.randint(30, 365)),
                    "deployment_date": timezone.now().date()
                    - timedelta(days=random.randint(1, 180))
                    if system_data["status"] == "deployed"
                    else None,
                },
            )

            if created:
                # Add technologies
                tech_names = system_data["technologies"]
                for tech_name in tech_names:
                    try:
                        tech = Technology.objects.get(name=tech_name)
                        system.technologies.add(tech)
                    except Technology.DoesNotExist:
                        pass

                created_systems.append(system)
                self.stdout.write(f"   ✅ Created system: {system.title}")

        return created_systems

    def _create_system_features(self):
        """Create realistic system features"""
        systems = SystemModule.objects.all()

        features_templates = [
            # Core features
            {
                "title": "User Authentication",
                "feature_type": "core",
                "implementation_status": "completed",
            },
            {
                "title": "RESTful API",
                "feature_type": "core",
                "implementation_status": "completed",
            },
            {
                "title": "Database Integration",
                "feature_type": "core",
                "implementation_status": "completed",
            },
            {
                "title": "Admin Dashboard",
                "feature_type": "core",
                "implementation_status": "completed",
            },
            # Advanced features
            {
                "title": "Real-time Updates",
                "feature_type": "advanced",
                "implementation_status": "completed",
            },
            {
                "title": "Data Analytics",
                "feature_type": "advanced",
                "implementation_status": "in_progress",
            },
            {
                "title": "Machine Learning Integration",
                "feature_type": "advanced",
                "implementation_status": "planned",
            },
            {
                "title": "Mobile App Support",
                "feature_type": "advanced",
                "implementation_status": "planned",
            },
            # Security features
            {
                "title": "OAuth Integration",
                "feature_type": "security",
                "implementation_status": "completed",
            },
            {
                "title": "Rate Limiting",
                "feature_type": "security",
                "implementation_status": "completed",
            },
            {
                "title": "Data Encryption",
                "feature_type": "security",
                "implementation_status": "tested",
            },
            # Performance features
            {
                "title": "Caching Layer",
                "feature_type": "performance",
                "implementation_status": "completed",
            },
            {
                "title": "Load Balancing",
                "feature_type": "performance",
                "implementation_status": "in_progress",
            },
            {
                "title": "Auto-scaling",
                "feature_type": "performance",
                "implementation_status": "planned",
            },
        ]

        for system in systems:
            # Randomly select 3-6 features per system
            selected_features = random.sample(features_templates, random.randint(3, 6))

            for i, feature_data in enumerate(selected_features):
                SystemFeature.objects.get_or_create(
                    system=system,
                    title=feature_data["title"],
                    defaults={
                        "description": f"{feature_data['title']} implementation for {system.title}",
                        "feature_type": feature_data["feature_type"],
                        "implementation_status": feature_data["implementation_status"],
                        "icon": "fas fa-check-circle",
                        "order": i,
                    },
                )

        self.stdout.write(
            f"   ✅ Created system features for {systems.count()} systems"
        )

    def _create_system_metrics(self):
        """Create realistic performance metrics"""
        systems = SystemModule.objects.filter(status__in=["deployed", "testing"])

        metric_types = [
            {"name": "Response Time", "unit": "ms", "type": "response_time"},
            {"name": "Uptime", "unit": "%", "type": "uptime"},
            {"name": "CPU Usage", "unit": "%", "type": "performance"},
            {"name": "Memory Usage", "unit": "MB", "type": "performance"},
            {"name": "Active Users", "unit": "users", "type": "usage"},
            {"name": "Error Rate", "unit": "%", "type": "error_rate"},
        ]

        for system in systems:
            for metric_type in metric_types:
                # Create metrics for the last 30 days
                for days_ago in range(30):
                    date = timezone.now() - timedelta(days=days_ago)

                    # Generate realistic metric values
                    if metric_type["name"] == "Response Time":
                        value = random.randint(80, 500)
                    elif metric_type["name"] == "Uptime":
                        value = random.uniform(95.0, 99.9)
                    elif metric_type["name"] == "CPU Usage":
                        value = random.uniform(20.0, 80.0)
                    elif metric_type["name"] == "Memory Usage":
                        value = random.randint(512, 2048)
                    elif metric_type["name"] == "Active Users":
                        value = random.randint(10, 1000)
                    elif metric_type["name"] == "Error Rate":
                        value = random.uniform(0.1, 2.0)

                    SystemMetric.objects.get_or_create(
                        system=system,
                        metric_name=metric_type["name"],
                        created_at=date,
                        defaults={
                            "metric_value": Decimal(str(round(value, 2))),
                            "metric_unit": metric_type["unit"],
                            "metric_type": metric_type["type"],
                            "is_current": days_ago == 0,
                        },
                    )

        self.stdout.write(f"   ✅ Created metrics for {systems.count()} systems")

    def _create_system_dependencies(self):
        """Create realistic system dependencies"""
        systems = list(SystemModule.objects.all())

        if len(systems) < 2:
            return

        # Create some realistic dependencies
        dependencies = [
            ("AURA Portfolio Platform", "TaskFlow API", "api", True),
            ("DataViz Analytics Platform", "TaskFlow API", "api", False),
            ("E-Commerce Analytics", "ML Model Pipeline", "service", False),
            ("DevOps Automation Suite", "TaskFlow API", "infrastructure", True),
        ]

        for system_name, depends_on_name, dep_type, is_critical in dependencies:
            try:
                system = SystemModule.objects.get(title=system_name)
                depends_on = SystemModule.objects.get(title=depends_on_name)

                SystemDependency.objects.get_or_create(
                    system=system,
                    depends_on=depends_on,
                    defaults={
                        "dependency_type": dep_type,
                        "is_critical": is_critical,
                        "description": f"{system.title} depends on {depends_on.title} for {dep_type} functionality",
                    },
                )
            except SystemModule.DoesNotExist:
                continue

        self.stdout.write(f"   ✅ Created system dependencies")

    def _create_blog_data(self, user, minimal=False):
        """Create blog categories, series, and posts"""
        # Create categories
        categories_data = [
            {
                "name": "Development",
                "code": "DEV",
                "color": "#00f0ff",
                "icon": "fas fa-code",
            },
            {
                "name": "Machine Learning",
                "code": "ML",
                "color": "#b39ddb",
                "icon": "fas fa-brain",
            },
            {
                "name": "DevOps",
                "code": "OPS",
                "color": "#a5d6a7",
                "icon": "fas fa-cogs",
            },
            {
                "name": "Tutorials",
                "code": "TUT",
                "color": "#fff59d",
                "icon": "fas fa-graduation-cap",
            },
        ]

        for cat_data in categories_data:
            Category.objects.get_or_create(
                name=cat_data["name"],
                defaults={
                    "slug": slugify(cat_data["name"]),
                    "code": cat_data["code"],
                    "color": cat_data["color"],
                    "icon": cat_data["icon"],
                    "description": f"Posts about {cat_data['name'].lower()}",
                },
            )

        # Create a series
        series, created = Series.objects.get_or_create(
            title="Django Portfolio Development",
            defaults={
                "slug": "django-portfolio-development",
                "description": "Building a professional portfolio with Django",
                "difficulty_level": "intermediate",
                "is_featured": True,
                "thumbnail": None,
                "post_count": 0,
                "total_reading_time": 0,
            },
        )

        # Create sample posts
        posts_data = [
            {
                "title": "Building the AURA Portfolio: Architecture Overview",
                "content": """
# AURA Portfolio Architecture

This post covers the high-level architecture decisions for the AURA portfolio platform.

## Technology Stack

- **Backend**: Django 4.2 with PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Caching**: Redis for session and query caching
- **Deployment**: AWS with Docker containers

## Key Design Principles

1. **Performance First**: Optimized queries and caching strategies
2. **Mobile Responsive**: Progressive enhancement approach
3. **Accessibility**: WCAG 2.1 AA compliance
4. **Security**: Industry best practices implementation

The system uses a modular approach with separate apps for core functionality, blog management, and project showcase.
                """,
                "category": "Development",
                "featured_code": """
# Django settings for AURA portfolio
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'aura_portfolio',
        'USER': 'postgres',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
                """,
                "featured_code_format": "python",
                "system": "AURA Portfolio Platform",
            },
            {
                "title": "Implementing Real-time Analytics Dashboard",
                "content": """
# Real-time Analytics Implementation

Building a real-time analytics dashboard requires careful consideration of data flow and user experience.

## WebSocket Integration

Using Django Channels for real-time updates:

```python
# consumers.py
class AnalyticsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("analytics", self.channel_name)
        await self.accept()

    async def analytics_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))
```

## Performance Considerations

- Efficient database queries with proper indexing
- Redis caching for frequently accessed data
- Pagination for large datasets
- Lazy loading for chart components

The dashboard provides real-time insights into system performance and user engagement metrics.
                """,
                "category": "Development",
                "featured_code": """
class SystemMetricsView(APIView):
    def get(self, request, system_id):
        system = get_object_or_404(SystemModule, id=system_id)
        metrics = system.metrics.filter(is_current=True)
        serializer = MetricsSerializer(metrics, many=True)
        return Response(serializer.data)
                """,
                "featured_code_format": "python",
                "system": "DataViz Analytics Platform",
            },
            {
                "title": "FastAPI Performance Optimization Techniques",
                "content": """
# FastAPI Performance Optimization

Optimizing FastAPI applications for high-throughput scenarios requires attention to several key areas.

## Async/Await Patterns

Proper use of async/await for I/O operations:

```python
@app.get("/tasks/{task_id}")
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

## Caching Strategies

- Redis for session data and frequently accessed objects
- Application-level caching for computed results
- Database query optimization with proper indexes

## Monitoring and Metrics

Using Prometheus metrics to track:
- Request latency and throughput
- Database connection pool usage
- Cache hit/miss ratios
- Error rates by endpoint

The TaskFlow API consistently maintains sub-100ms response times under normal load conditions.
                """,
                "category": "Development",
                "featured_code": """
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
                """,
                "featured_code_format": "python",
                "system": "TaskFlow API",
            },
            {
                "title": "Machine Learning Pipeline Automation",
                "content": """
# Automated ML Pipeline Implementation

Building robust machine learning pipelines requires careful orchestration of data processing, training, and deployment phases.

## Pipeline Architecture

The ML pipeline consists of several key components:

1. **Data Ingestion**: Automated data collection from multiple sources
2. **Data Validation**: Schema validation and data quality checks
3. **Feature Engineering**: Automated feature extraction and transformation
4. **Model Training**: Hyperparameter tuning and cross-validation
5. **Model Validation**: Performance testing and drift detection
6. **Deployment**: Automated model deployment with A/B testing

## MLflow Integration

Using MLflow for experiment tracking and model versioning:

```python
import mlflow
import mlflow.sklearn

with mlflow.start_run():
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)

    # Log metrics
    mlflow.log_metric("accuracy", accuracy_score(y_test, predictions))
    mlflow.log_metric("f1_score", f1_score(y_test, predictions))

    # Log model
    mlflow.sklearn.log_model(model, "model")
```

## Monitoring and Alerting

The pipeline includes comprehensive monitoring for:
- Data drift detection
- Model performance degradation
- Infrastructure health metrics
- Training job success/failure rates

Automated retraining is triggered when performance drops below defined thresholds.
                """,
                "category": "Machine Learning",
                "featured_code": """
class ModelPipeline:
    def __init__(self, config):
        self.config = config
        self.mlflow_client = MlflowClient()
    
    async def train_model(self, data):
        with mlflow.start_run():
            # Feature engineering
            features = self.preprocess_data(data)
            
            # Model training
            model = self.train(features)
            
            # Validation
            metrics = self.validate(model, features)
            
            # Log everything
            self.log_artifacts(model, metrics)
            
            return model
                """,
                "featured_code_format": "python",
                "system": "ML Model Pipeline",
            },
            {
                "title": "DevOps Automation with Infrastructure as Code",
                "content": """
# Infrastructure as Code with Terraform

Implementing DevOps automation requires a systematic approach to infrastructure management.

## Terraform Configuration

Managing cloud infrastructure with declarative configuration:

```hcl
resource "aws_ecs_cluster" "main" {
  name = var.cluster_name
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_service" "app" {
  name            = var.service_name
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = var.desired_count
  
  deployment_configuration {
    maximum_percent         = 200
    minimum_healthy_percent = 100
  }
}
```

## CI/CD Pipeline

GitHub Actions workflow for automated deployment:

- Code quality checks (linting, testing)
- Security scanning with SAST tools
- Docker image building and scanning
- Infrastructure deployment validation
- Application deployment with zero downtime

## Monitoring and Observability

Comprehensive monitoring stack including:
- Prometheus for metrics collection
- Grafana for visualization and alerting
- ELK stack for centralized logging
- Distributed tracing with Jaeger

The automation suite handles deployments across multiple environments with consistent configuration.
                """,
                "category": "DevOps",
                "featured_code": """
# GitHub Actions workflow
name: Deploy to Production
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      
      - name: Deploy with Terraform
        run: |
          terraform init
          terraform plan -out=tfplan
          terraform apply tfplan
                """,
                "featured_code_format": "yaml",
                "system": "DevOps Automation Suite",
            },
        ]

        if minimal:
            posts_data = posts_data[:2]

        systems = {sys.title: sys for sys in SystemModule.objects.all()}

        for i, post_data in enumerate(posts_data):
            category = Category.objects.get(name=post_data["category"])

            post, created = Post.objects.get_or_create(
                title=post_data["title"],
                defaults={
                    "slug": slugify(post_data["title"]),
                    "content": post_data["content"],
                    "excerpt": post_data["content"][:200] + "...",
                    "author": user,
                    "category": category,
                    "status": "published",
                    "published_date": timezone.now()
                    - timedelta(days=random.randint(1, 60)),
                    "reading_time": random.randint(3, 8),
                    "featured": i < 2,
                    "featured_code": post_data.get("featured_code", ""),
                    "featured_code_format": post_data.get(
                        "featured_code_format", "python"
                    ),
                },
            )

            if created and post_data.get("system") in systems:
                # Create system log entry
                system = systems[post_data["system"]]
                SystemLogEntry.objects.create(
                    post=post,
                    system=system,
                    connection_type="documentation",
                    priority=random.randint(1, 4),
                    log_entry_id=f"SYS-{system.id:03d}-LOG-{i + 1:03d}",
                    system_version=f"v{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
                    impact_level=random.choice(["low", "medium", "high"]),
                    estimated_hours=random.randint(2, 8),
                    actual_hours=random.randint(1, 10),
                )

        self.stdout.write(f"   ✅ Created blog data with {Post.objects.count()} posts")

    def _create_core_skills(self, limit=None):
        """Create enhanced skills with all new fields"""
        skills_data = [
            # Programming Languages
            {
                "name": "Python",
                "category": "languages",
                "proficiency": 5,
                "icon": "fab fa-python",
                "color": "#3776ab",
                "years_experience": 5.0,
                "is_featured": True,
                "is_certified": True,
            },
            {
                "name": "JavaScript",
                "category": "languages",
                "proficiency": 4,
                "icon": "fab fa-js-square",
                "color": "#f7df1e",
                "years_experience": 4.0,
                "is_featured": True,
                "is_certified": False,
            },
            {
                "name": "TypeScript",
                "category": "languages",
                "proficiency": 4,
                "icon": "fab fa-js-square",
                "color": "#3178c6",
                "years_experience": 2.5,
                "is_featured": True,
                "is_certified": False,
            },
            {
                "name": "SQL",
                "category": "languages",
                "proficiency": 4,
                "icon": "fas fa-database",
                "color": "#336791",
                "years_experience": 4.5,
                "is_featured": True,
                "is_certified": True,
            },
            # Frameworks & Libraries
            {
                "name": "Django",
                "category": "frameworks",
                "proficiency": 5,
                "icon": "fab fa-python",
                "color": "#092e20",
                "years_experience": 4.0,
                "is_featured": True,
                "is_certified": False,
            },
            {
                "name": "Flask",
                "category": "frameworks",
                "proficiency": 4,
                "icon": "fab fa-python",
                "color": "#000000",
                "years_experience": 3.0,
                "is_featured": False,
                "is_certified": False,
            },
            {
                "name": "FastAPI",
                "category": "frameworks",
                "proficiency": 4,
                "icon": "fas fa-bolt",
                "color": "#009688",
                "years_experience": 2.0,
                "is_featured": True,
                "is_certified": False,
            },
            {
                "name": "React",
                "category": "frameworks",
                "proficiency": 4,
                "icon": "fab fa-react",
                "color": "#61dafb",
                "years_experience": 3.0,
                "is_featured": True,
                "is_certified": False,
            },
            {
                "name": "Vue.js",
                "category": "frameworks",
                "proficiency": 3,
                "icon": "fab fa-vuejs",
                "color": "#4fc08d",
                "years_experience": 1.5,
                "is_featured": False,
                "is_certified": False,
            },
            # Databases
            {
                "name": "PostgreSQL",
                "category": "databases",
                "proficiency": 4,
                "icon": "fas fa-database",
                "color": "#336791",
                "years_experience": 4.0,
                "is_featured": True,
                "is_certified": True,
            },
            {
                "name": "Redis",
                "category": "databases",
                "proficiency": 3,
                "icon": "fas fa-memory",
                "color": "#dc382d",
                "years_experience": 2.5,
                "is_featured": False,
                "is_certified": False,
            },
            {
                "name": "MongoDB",
                "category": "databases",
                "proficiency": 3,
                "icon": "fas fa-leaf",
                "color": "#47a248",
                "years_experience": 2.0,
                "is_featured": False,
                "is_certified": False,
            },
            # Tools & Technologies
            {
                "name": "Git",
                "category": "tools",
                "proficiency": 5,
                "icon": "fab fa-git-alt",
                "color": "#f05032",
                "years_experience": 6.0,
                "is_featured": True,
                "is_certified": False,
            },
            {
                "name": "Docker",
                "category": "tools",
                "proficiency": 4,
                "icon": "fab fa-docker",
                "color": "#2496ed",
                "years_experience": 3.0,
                "is_featured": True,
                "is_certified": True,
            },
            {
                "name": "AWS",
                "category": "tools",
                "proficiency": 3,
                "icon": "fab fa-aws",
                "color": "#ff9900",
                "years_experience": 2.5,
                "is_featured": True,
                "is_certified": True,
            },
            {
                "name": "Kubernetes",
                "category": "tools",
                "proficiency": 3,
                "icon": "fas fa-dharmachakra",
                "color": "#326ce5",
                "years_experience": 1.5,
                "is_featured": False,
                "is_certified": False,
            },
            # Other Skills
            {
                "name": "API Design",
                "category": "other",
                "proficiency": 5,
                "icon": "fas fa-plug",
                "color": "#26c6da",
                "years_experience": 4.0,
                "is_featured": True,
                "is_certified": False,
            },
            {
                "name": "Database Design",
                "category": "other",
                "proficiency": 4,
                "icon": "fas fa-sitemap",
                "color": "#ff8a80",
                "years_experience": 4.0,
                "is_featured": False,
                "is_certified": False,
            },
            {
                "name": "System Architecture",
                "category": "other",
                "proficiency": 4,
                "icon": "fas fa-project-diagram",
                "color": "#b39ddb",
                "years_experience": 3.5,
                "is_featured": True,
                "is_certified": False,
            },
            {
                "name": "DevOps",
                "category": "other",
                "proficiency": 3,
                "icon": "fas fa-cogs",
                "color": "#a5d6a7",
                "years_experience": 2.0,
                "is_featured": False,
                "is_certified": False,
            },
        ]

        if limit:
            skills_data = skills_data[:limit]

        # Link skills to technologies where possible
        technologies = {tech.name: tech for tech in Technology.objects.all()}

        for i, skill_data in enumerate(skills_data):
            skill, created = Skill.objects.get_or_create(
                name=skill_data["name"],
                defaults={
                    "slug": slugify(skill_data["name"]),
                    "category": skill_data["category"],
                    "proficiency": skill_data["proficiency"],
                    "icon": skill_data["icon"],
                    "color": skill_data["color"],
                    "display_order": i,
                    "description": f"Professional experience with {skill_data['name']}",
                    # Enhanced fields
                    "years_experience": skill_data["years_experience"],
                    "is_featured": skill_data["is_featured"],
                    "is_currently_learning": random.choice([True, False])
                    if skill_data["proficiency"] < 5
                    else False,
                    "is_certified": skill_data["is_certified"],
                    "last_used": date.today() - timedelta(days=random.randint(1, 365))
                    if not skill_data["is_featured"]
                    else date.today(),
                    # Link to technology if exists
                    "related_technology": technologies.get(skill_data["name"]),
                },
            )
            if created:
                self.stdout.write(f"   ✅ Created skill: {skill.name}")

    def _create_portfolio_analytics(self):
        """Create sample portfolio analytics data"""
        # Create analytics for the last 30 days
        for days_ago in range(30):
            analytics_date = date.today() - timedelta(days=days_ago)

            # Generate realistic analytics data
            unique_visitors = random.randint(50, 200)
            page_views = unique_visitors * random.randint(2, 5)
            bounce_rate = random.uniform(30.0, 70.0)
            avg_session = random.randint(60, 300)

            # Get random top content
            posts = list(Post.objects.all())
            systems = list(SystemModule.objects.all())

            PortfolioAnalytics.objects.get_or_create(
                date=analytics_date,
                defaults={
                    "unique_visitors": unique_visitors,
                    "page_views": page_views,
                    "bounce_rate": bounce_rate,
                    "avg_session_duration": avg_session,
                    "datalog_views": random.randint(20, 100),
                    "system_views": random.randint(15, 80),
                    "contact_form_submissions": random.randint(0, 5),
                    "github_clicks": random.randint(5, 30),
                    "top_datalog": random.choice(posts) if posts else None,
                    "top_system": random.choice(systems) if systems else None,
                    "top_country": random.choice(
                        [
                            "United States",
                            "Canada",
                            "United Kingdom",
                            "Germany",
                            "Australia",
                        ]
                    ),
                    "top_city": random.choice(
                        ["New York", "San Francisco", "London", "Berlin", "Toronto"]
                    ),
                    "top_referrer": random.choice(
                        ["Google", "GitHub", "LinkedIn", "Direct", "Twitter"]
                    ),
                    "organic_search_percentage": random.uniform(40.0, 80.0),
                },
            )

        self.stdout.write(f"   ✅ Created 30 days of portfolio analytics")

    def _create_sample_contacts(self):
        """Create sample contact form submissions"""
        contact_templates = [
            {
                "name": "Sarah Chen",
                "email": "sarah.chen@techcorp.com",
                "subject": "Collaboration Opportunity",
                "message": "Hi! I came across your portfolio and was impressed by your Django work. We have an exciting project that might be a good fit for your skills. Would you be interested in discussing a potential collaboration?",
                "inquiry_category": "collaboration",
                "priority": "high",
            },
            {
                "name": "Mike Rodriguez",
                "email": "mike.r@startup.io",
                "subject": "Technical Question about FastAPI",
                "message": "I read your blog post about FastAPI optimization and had a question about async database connections. Could you share more details about your approach to connection pooling?",
                "inquiry_category": "question",
                "priority": "normal",
            },
            {
                "name": "Jennifer Liu",
                "email": "j.liu@consulting.com",
                "subject": "Freelance Project Inquiry",
                "message": "We have a client who needs a data analytics dashboard similar to what you showcased. The timeline is flexible and the budget is competitive. Are you available for freelance work?",
                "inquiry_category": "project",
                "priority": "high",
            },
            {
                "name": "David Park",
                "email": "david.park@university.edu",
                "subject": "Guest Speaking Opportunity",
                "message": "Would you be interested in speaking at our university's tech symposium about modern web development? We can cover travel expenses and provide an honorarium.",
                "inquiry_category": "other",
                "priority": "normal",
            },
            {
                "name": "Alex Thompson",
                "email": "alex@devcompany.com",
                "subject": "Feedback on Portfolio",
                "message": "Really impressive portfolio! The HUD design is unique and the technical depth of your projects shows real expertise. Keep up the great work!",
                "inquiry_category": "feedback",
                "priority": "low",
            },
        ]

        for i, contact_data in enumerate(contact_templates):
            Contact.objects.get_or_create(
                email=contact_data["email"],
                defaults={
                    "name": contact_data["name"],
                    "subject": contact_data["subject"],
                    "message": contact_data["message"],
                    "inquiry_category": contact_data["inquiry_category"],
                    "priority": contact_data["priority"],
                    "is_read": random.choice([True, False]),
                    "response_sent": random.choice([True, False]),
                    "response_date": timezone.now()
                    - timedelta(days=random.randint(1, 10))
                    if random.choice([True, False])
                    else None,
                    "referrer_page": random.choice(
                        ["/projects/", "/blog/", "/", "/contact/"]
                    ),
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                },
            )

        self.stdout.write(f"   ✅ Created {len(contact_templates)} sample contacts")

    def _display_summary(self):
        """Display creation summary"""
        self.stdout.write(
            self.style.SUCCESS("✅ Successfully created enhanced portfolio data!")
        )
        self.stdout.write("📊 Summary:")
        self.stdout.write(f"   • {SystemModule.objects.count()} Systems")
        self.stdout.write(f"   • {Technology.objects.count()} Technologies")
        self.stdout.write(f"   • {SystemType.objects.count()} System Types")
        self.stdout.write(f"   • {SystemFeature.objects.count()} System Features")
        self.stdout.write(f"   • {SystemMetric.objects.count()} System Metrics")
        self.stdout.write(
            f"   • {SystemDependency.objects.count()} System Dependencies"
        )
        self.stdout.write(f"   • {Post.objects.count()} Blog Posts")
        self.stdout.write(f"   • {Category.objects.count()} Blog Categories")
        self.stdout.write(f"   • {Skill.objects.count()} Skills")
        self.stdout.write(
            f"   • {PortfolioAnalytics.objects.count()} Analytics Records"
        )
        self.stdout.write(f"   • {Contact.objects.count()} Contact Messages")

        self.stdout.write("\n🎯 Next Steps:")
        self.stdout.write("   • Check the admin interface to see all the enhanced data")
        self.stdout.write(
            "   • Explore the relationships between systems, skills, and technologies"
        )
        self.stdout.write("   • Review the sample analytics and performance metrics")
        self.stdout.write("   • Start building the frontend views and templates!")
