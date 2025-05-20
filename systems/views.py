from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404
from django.http import Http404


from .models import System, Category, Technology


class SystemListView(ListView):
    """View for displaying all systems/projects."""
    model = System
    template_name = 'systems/systems.html'
    context_object_name = 'projects'  # Using ;projects for template consistency

    def get_queryset(self):
        # Temporary placeholder data
        # Replace with actual model query when ready
        return [
            {
                "id": 1,
                "title": "AI-Powered Data Analysis Platform",
                "slug": "ai-data-analysis",
                "description": "Real-time data processing system using Python, Django, and machine learning algorithms to analyze large datasets.",
                "completion_percentage": 95,
                "technologies": [
                    {"name": "Python"},
                    {"name": "Django"},
                    {"name": "TensorFlow"},
                    {"name": "PostgreSQL"},
                ],
                "category": {"name": "Data Science"},
                "featured": True,
            },
            {
                "id": 2,
                "title": "Automated Task Management System",
                "slug": "task-management",
                "description": "Django application for task delegation, tracking, and automation with integrated notification system.",
                "completion_percentage": 85,
                "technologies": [
                    {"name": "Python"},
                    {"name": "Django"},
                    {"name": "Celery"},
                    {"name": "Redis"},
                ],
                "category": {"name": "Web Development"},
                "featured": False,
            },
            {
                "id": 3,
                "title": "Financial Data Visualization Dashboard",
                "slug": "financial-dashboard",
                "description": "Interactive dashboard for visualizing financial data with customizable charts and reports.",
                "completion_percentage": 75,
                "technologies": [
                    {"name": "Python"},
                    {"name": "Django"},
                    {"name": "D3.js"},
                    {"name": "PostgreSQL"},
                ],
                "category": {"name": "Data Visualization"},
                "featured": True,
            },
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add categories for filtering
        context["categories"] = [
            {"name": "All", "slug": ""},
            {"name": "Data Science", "slug": "data-science"},
            {"name": "Web Development", "slug": "web-development"},
            {"name": "Data Visualization", "slug": "data-visualization"},
        ]

        # Selected category (if filtering)
        selected_category = self.kwargs.get("category", None)
        context["selected_category"] = next(
            (cat for cat in context["categories"] if cat["slug"] == selected_category),
            None,
        )

        return context


class SystemCategoryView(SystemListView):
    """View for displaying systems filtered by category."""

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.kwargs.get('category', '')

        # Filter projects by category
        if category_slug:
            queryset = [p for p in queryset if p['category']['name'].lower().replace(' ','-') == category_slug]

        return queryset


class SystemDetailView(DetailView):
    """View for displaying a single system/project."""
    model = System
    template_name = 'systems/system_detail.html'
    context_object_name = 'project'  # Using 'project' here for template consistency

    def get_object(self):
        # Temporary placeholder data
        # Replace with actual model retrieval when ready
        slug = self.kwargs.get("slug")

        projects = [
            {
                "id": 1,
                "title": "AI-Powered Data Analysis Platform",
                "slug": "ai-data-analysis",
                "description": "Real-time data processing system using Python, Django, and machine learning algorithms to analyze large datasets.",
                "completion_percentage": 95,
                "content": """
                ## System Overview
                
                This AI-powered data analysis platform provides real-time processing and visualization of large datasets using machine learning algorithms. Built with Python and Django, the system can handle structured and unstructured data from various sources.
                
                ## Key Features
                
                * Real-time data ingestion pipeline
                * Machine learning-based classification
                * Customizable dashboards
                * Automated reporting system
                * API integration capabilities
                
                ## Technical Architecture
                
                The platform follows a microservices architecture with containerized components for scalability. Data is processed through a pipeline that includes preprocessing, analysis, and visualization stages.
                """,
                "technologies": [
                    {"name": "Python", "percentage": 45},
                    {"name": "Django", "percentage": 30},
                    {"name": "TensorFlow", "percentage": 15},
                    {"name": "PostgreSQL", "percentage": 10},
                ],
                "category": {"name": "Data Science"},
                "github_url": "https://github.com/yourusername/ai-data-analysis",
                "live_url": "https://example.com/ai-platform",
                "status": "Active",
                "created_at": "2024-12-01",
                "updated_at": "2025-04-10",
                "images": [
                    {
                        "image": {"url": "/static/img/placeholder-1.jpg"},
                        "caption": "Dashboard Interface",
                    },
                    {
                        "image": {"url": "/static/img/placeholder-2.jpg"},
                        "caption": "Data Pipeline Visualization",
                    },
                ],
            },
            {
                "id": 2,
                "title": "Automated Task Management System",
                "slug": "task-management",
                "description": "Django application for task delegation, tracking, and automation with integrated notification system.",
                "completion_percentage": 85,
                "content": """
                ## System Overview
                
                The Automated Task Management System is a comprehensive solution for organizations to streamline task delegation, tracking, and automation. Built with Django, it provides real-time updates and notifications.
                
                ## Key Features
                
                * Task creation and assignment
                * Deadline management
                * Automated notifications
                * Progress tracking
                * Reporting dashboard
                
                ## Technical Architecture
                
                The application follows a standard Django MVT architecture with Celery for background task processing and Redis for message queuing.
                """,
                "technologies": [
                    {"name": "Python", "percentage": 40},
                    {"name": "Django", "percentage": 35},
                    {"name": "Celery", "percentage": 15},
                    {"name": "Redis", "percentage": 10},
                ],
                "category": {"name": "Web Development"},
                "github_url": "https://github.com/yourusername/task-management",
                "live_url": "https://example.com/task-system",
                "status": "Active",
                "created_at": "2024-08-15",
                "updated_at": "2025-03-20",
                "images": [
                    {
                        "image": {"url": "/static/img/placeholder-3.jpg"},
                        "caption": "Task Dashboard",
                    },
                    {
                        "image": {"url": "/static/img/placeholder-4.jpg"},
                        "caption": "Notification System",
                    },
                ],
            },
            {
                "id": 3,
                "title": "Financial Data Visualization Dashboard",
                "slug": "financial-dashboard",
                "description": "Interactive dashboard for visualizing financial data with customizable charts and reports.",
                "completion_percentage": 75,
                "content": """
                ## System Overview
                
                The Financial Data Visualization Dashboard provides an interactive interface for analyzing and visualizing financial data. Users can create customized charts and reports based on various financial metrics.
                
                ## Key Features
                
                * Interactive data visualizations
                * Customizable dashboard layouts
                * Data import/export functionality
                * Automated report generation
                * Historical trend analysis
                
                ## Technical Architecture
                
                Built with Django on the backend and D3.js for frontend visualizations, the system uses PostgreSQL for data storage and includes a RESTful API for data access.
                """,
                "technologies": [
                    {"name": "Python", "percentage": 35},
                    {"name": "Django", "percentage": 30},
                    {"name": "D3.js", "percentage": 25},
                    {"name": "PostgreSQL", "percentage": 10},
                ],
                "category": {"name": "Data Visualization"},
                "github_url": "https://github.com/yourusername/financial-dashboard",
                "live_url": "https://example.com/finance-dashboard",
                "status": "In Development",
                "created_at": "2025-01-10",
                "updated_at": "2025-05-01",
                "images": [
                    {
                        "image": {"url": "/static/img/placeholder-5.jpg"},
                        "caption": "Financial Charts",
                    },
                    {
                        "image": {"url": "/static/img/placeholder-6.jpg"},
                        "caption": "Report Generator Interface",
                    },
                ],
            },
        ]

        # Find the project with matching slug
        project = next((p for p in projects if p["slug"] == slug), None)
        if not project:
            raise Http404(f"System with slug '{slug}' does not exist")

        return project