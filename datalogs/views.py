from django.views.generic import ListView, DetailView, DeleteView, CreateView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.db.models import Count
from markdownx.utils import markdownify

from datetime import datetime
import calendar
import os
import re
from uuid import uuid4
import pprint

from .models import DataLog, Category, Tag, Series, SeriesLogEntry
# from .forms import PostForm, CategoryForm, TagForm, SeriesForm


class DataLogListView(ListView):
    """View for displaying all data logs."""

    model = DataLog
    template_name = "datalogs/datalogs.html"
    context_object_name = "posts"  # Using 'posts' for template consistency
    paginate_by = 5

    def get_queryset(self):
        # Temporary placeholder data
        # Replace with actual model query when ready
        return [
            {
                "id": 1,
                "title": "Building Efficient Data Pipelines",
                "slug": "building-data-pipelines",
                "excerpt": "A comprehensive guide to designing and implementing efficient data pipelines using Python, Apache Airflow, and related technologies.",
                "created_at": "2025-05-10",
                "tags": [
                    {"name": "Python", "slug": "python"},
                    {"name": "Data Engineering", "slug": "data-engineering"},
                    {"name": "Airflow", "slug": "airflow"},
                ],
            },
            {
                "id": 2,
                "title": "Django ORM Optimization Techniques",
                "slug": "django-orm-optimization",
                "excerpt": "Advanced strategies for optimizing Django ORM queries to improve performance in large-scale applications.",
                "created_at": "2025-05-05",
                "tags": [
                    {"name": "Django", "slug": "django"},
                    {"name": "Performance", "slug": "performance"},
                    {"name": "Database", "slug": "database"},
                ],
            },
            {
                "id": 3,
                "title": "Machine Learning Model Deployment",
                "slug": "ml-model-deployment",
                "excerpt": "Best practices for deploying machine learning models in production using containerization and CI/CD pipelines.",
                "created_at": "2025-04-28",
                "tags": [
                    {"name": "Machine Learning", "slug": "machine-learning"},
                    {"name": "DevOps", "slug": "devops"},
                    {"name": "Docker", "slug": "docker"},
                ],
            },
            {
                "id": 4,
                "title": "RESTful API Design Principles",
                "slug": "restful-api-design",
                "excerpt": "A deep dive into RESTful API design principles and best practices for creating robust, scalable APIs.",
                "created_at": "2025-04-15",
                "tags": [
                    {"name": "API", "slug": "api"},
                    {"name": "REST", "slug": "rest"},
                    {"name": "Web Development", "slug": "web-development"},
                ],
            },
            {
                "id": 5,
                "title": "Python Concurrency Explained",
                "slug": "python-concurrency",
                "excerpt": "Understanding Python's concurrency models including threading, multiprocessing, and asynchronous programming.",
                "created_at": "2025-04-05",
                "tags": [
                    {"name": "Python", "slug": "python"},
                    {"name": "Concurrency", "slug": "concurrency"},
                    {"name": "Performance", "slug": "performance"},
                ],
            },
            {
                "id": 6,
                "title": "Test-Driven Development with Python",
                "slug": "tdd-python",
                "excerpt": "A practical guide to implementing Test-Driven Development methodology in Python projects.",
                "created_at": "2025-03-25",
                "tags": [
                    {"name": "Python", "slug": "python"},
                    {"name": "Testing", "slug": "testing"},
                    {"name": "TDD", "slug": "tdd"},
                ],
            },
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add all tags for filtering
        context["tags"] = [
            {"name": "Python", "slug": "python"},
            {"name": "Django", "slug": "django"},
            {"name": "Data Engineering", "slug": "data-engineering"},
            {"name": "Machine Learning", "slug": "machine-learning"},
            {"name": "API", "slug": "api"},
            {"name": "Performance", "slug": "performance"},
            {"name": "Testing", "slug": "testing"},
            {"name": "DevOps", "slug": "devops"},
        ]

        # Selected tag (if filtering)
        selected_tag = self.kwargs.get("tag", None)
        context["selected_tag"] = next(
            (tag for tag in context["tags"] if tag["slug"] == selected_tag), None
        )

        return context


class DataLogTagView(DataLogListView):
    """View for displaying data logs filtered by tag."""

    def get_queryset(self):
        queryset = super().get_queryset()
        tag_slug = self.kwargs.get("tag", "")

        # Filter logs by tag
        if tag_slug:
            queryset = [
                p for p in queryset if any(t["slug"] == tag_slug for t in p["tags"])
            ]

        return queryset


class DataLogDetailView(DetailView):
    """View for displaying a single data log."""

    # model = DataLog  # Uncomment when model is ready
    template_name = "datalogs/datalog_detail.html"
    context_object_name = "post"  # Using 'post' for template consistency

    def get_object(self):
        # Temporary placeholder data
        # Replace with actual model retrieval when ready
        slug = self.kwargs.get("slug")

        posts = [
            {
                "id": 1,
                "title": "Building Efficient Data Pipelines",
                "slug": "building-data-pipelines",
                "excerpt": "A comprehensive guide to designing and implementing efficient data pipelines using Python, Apache Airflow, and related technologies.",
                "content": """
                ## Introduction
                
                Data pipelines are essential components of modern data infrastructure, enabling seamless data movement between systems. Efficient pipelines ensure data is processed, transformed, and delivered reliably and in a timely manner.
                
                ## Key Components
                
                1. **Data Extraction**: Pulling data from various sources
                2. **Data Transformation**: Cleaning, enriching, and restructuring data
                3. **Data Loading**: Storing processed data in destination systems
                4. **Orchestration**: Coordinating pipeline tasks and dependencies
                5. **Monitoring**: Tracking pipeline performance and detecting failures
                
                ## Pipeline Orchestration with Apache Airflow
                
                Apache Airflow has become the de facto standard for data pipeline orchestration due to its flexibility and robust feature set.
                
                ```python
                from datetime import datetime, timedelta
                from airflow import DAG
                from airflow.operators.python_operator import PythonOperator
                
                default_args = {
                    'owner': 'data_engineer',
                    'depends_on_past': False,
                    'start_date': datetime(2025, 1, 1),
                    'email_on_failure': True,
                    'email_on_retry': False,
                    'retries': 3,
                    'retry_delay': timedelta(minutes=5)
                }
                
                dag = DAG(
                    'example_data_pipeline',
                    default_args=default_args,
                    description='A simple data pipeline example',
                    schedule_interval='@daily'
                )
                
                def extract_data(**kwargs):
                    # Data extraction logic
                    pass
                
                def transform_data(**kwargs):
                    # Data transformation logic
                    pass
                
                def load_data(**kwargs):
                    # Data loading logic
                    pass
                
                extract_task = PythonOperator(
                    task_id='extract_data',
                    python_callable=extract_data,
                    dag=dag
                )
                
                transform_task = PythonOperator(
                    task_id='transform_data',
                    python_callable=transform_data,
                    dag=dag
                )
                
                load_task = PythonOperator(
                    task_id='load_data',
                    python_callable=load_data,
                    dag=dag
                )
                
                extract_task >> transform_task >> load_task
                ```
                
                ## Optimization Techniques
                
                1. **Incremental Processing**: Only process new or changed data
                2. **Parallelization**: Distribute processing across multiple workers
                3. **Caching**: Store intermediate results to avoid recomputation
                4. **Resource Management**: Allocate resources based on task requirements
                
                ## Conclusion
                
                Building efficient data pipelines requires careful planning, the right tools, and continuous optimization. By following these best practices, you can create robust pipelines that scale with your data needs.
                """,
                "created_at": "2025-05-10",
                "tags": [
                    {"name": "Python", "slug": "python"},
                    {"name": "Data Engineering", "slug": "data-engineering"},
                    {"name": "Airflow", "slug": "airflow"},
                ],
            },
            {
                "id": 2,
                "title": "Django ORM Optimization Techniques",
                "slug": "django-orm-optimization",
                "excerpt": "Advanced strategies for optimizing Django ORM queries to improve performance in large-scale applications.",
                "content": """
                ## Introduction
                
                Django's Object-Relational Mapping (ORM) provides a convenient abstraction for database operations, but inefficient queries can lead to performance bottlenecks in large-scale applications. This guide covers advanced optimization techniques to ensure your Django application performs efficiently.
                
                ## Common Performance Issues
                
                1. **N+1 Query Problem**: Making additional queries for each result
                2. **Retrieving Unnecessary Data**: Selecting all fields when only a few are needed
                3. **Inefficient Filtering**: Using non-indexed fields in filter conditions
                4. **Database Load**: Performing operations in Python instead of the database
                
                ## Optimization Techniques
                
                ### 1. Using `select_related` and `prefetch_related`
                
                The `select_related` method allows you to retrieve related objects in a single database query using a SQL JOIN.
                
                ```python
                # Instead of this (causes N+1 queries)
                orders = Order.objects.all()
                for order in orders:
                    customer = order.customer  # This triggers a separate query
                
                # Do this (single query with JOIN)
                orders = Order.objects.select_related('customer').all()
                for order in orders:
                    customer = order.customer  # No additional query
                ```
                
                For many-to-many relationships, use `prefetch_related`:
                
                ```python
                # Efficient way to fetch products and their categories
                products = Product.objects.prefetch_related('categories').all()
                ```
                
                ### 2. Deferring Unnecessary Fields
                
                When you don't need all fields from a model, use `only()` or `defer()`:
                
                ```python
                # Only retrieve necessary fields
                users = User.objects.only('id', 'username', 'email')
                
                # Defer large fields
                articles = Article.objects.defer('content')
                ```
                
                ### 3. Using Database Functions
                
                Leverage database functions to perform operations at the database level:
                
                ```python
                from django.db.models import F, Sum, Count
                
                # Instead of updating in Python
                for product in products:
                    product.price = product.price * 1.1
                    product.save()
                
                # Do this (single UPDATE query)
                Product.objects.update(price=F('price') * 1.1)
                
                # Aggregations at database level
                total_sales = Order.objects.aggregate(total=Sum('amount'))
                ```
                
                ### 4. Query Optimization with `exists()` and `values()`
                
                Use `exists()` to check for existence without fetching data:
                
                ```python
                # Instead of this
                if Product.objects.filter(category=category).count() > 0:
                    # Do something
                
                # Do this
                if Product.objects.filter(category=category).exists():
                    # Do something
                ```
                
                Use `values()` or `values_list()` when you need dictionary/list results:
                
                ```python
                # Get list of product names
                product_names = Product.objects.values_list('name', flat=True)
                ```
                
                ## Monitoring Query Performance
                
                Always monitor your application's query performance using:
                
                1. Django Debug Toolbar for development
                2. Database query logs for production analysis
                3. Performance monitoring tools
                
                ## Conclusion
                
                Optimizing Django ORM queries is crucial for building scalable applications. By understanding how the ORM translates to SQL and applying these techniques, you can significantly improve your application's performance.
                """,
                "created_at": "2025-05-05",
                "tags": [
                    {"name": "Django", "slug": "django"},
                    {"name": "Performance", "slug": "performance"},
                    {"name": "Database", "slug": "database"},
                ],
            },
            {
                "id": 3,
                "title": "Machine Learning Model Deployment",
                "slug": "ml-model-deployment",
                "excerpt": "Best practices for deploying machine learning models in production using containerization and CI/CD pipelines.",
                "content": """
                ## Introduction
                
                Deploying machine learning models to production environments is a critical step in the ML lifecycle. This guide covers best practices for deploying models reliably and efficiently using containerization and CI/CD pipelines.
                
                ## Key Challenges in ML Deployment
                
                1. **Environment Reproducibility**: Ensuring consistent behavior across different environments
                2. **Scalability**: Handling varying load demands efficiently
                3. **Monitoring**: Tracking model performance and detecting drift
                4. **Versioning**: Managing model versions and facilitating rollbacks
                
                ## Containerization with Docker
                
                Docker containers provide a consistent environment for your ML models:
                
                ```dockerfile
                FROM python:3.9-slim
                
                WORKDIR /app
                
                COPY requirements.txt .
                RUN pip install --no-cache-dir -r requirements.txt
                
                COPY . .
                
                # Load model during container build
                RUN python -c "import pickle; import os; \
                    os.makedirs('models', exist_ok=True); \
                    from model import train_model; \
                    model = train_model(); \
                    with open('models/model.pkl', 'wb') as f: \
                    pickle.dump(model, f)"
                
                EXPOSE 8000
                
                CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
                ```
                
                ## API Development for Model Serving
                
                Use FastAPI to create a robust API for serving predictions:
                
                ```python
                from fastapi import FastAPI, HTTPException
                from pydantic import BaseModel
                import pickle
                import numpy as np
                
                # Load model
                with open("models/model.pkl", "rb") as f:
                    model = pickle.load(f)
                
                app = FastAPI(title="ML Model API")
                
                class PredictionInput(BaseModel):
                    features: list[float]
                
                class PredictionOutput(BaseModel):
                    prediction: float
                    probability: float
                
                @app.post("/predict", response_model=PredictionOutput)
                def predict(input_data: PredictionInput):
                    try:
                        features = np.array(input_data.features).reshape(1, -1)
                        prediction = model.predict(features)[0]
                        probability = model.predict_proba(features).max()
                        
                        return {
                            "prediction": float(prediction),
                            "probability": float(probability)
                        }
                    except Exception as e:
                        raise HTTPException(status_code=500, detail=str(e))
                ```
                
                ## CI/CD Pipeline for ML Models
                
                A typical CI/CD pipeline for ML models includes:
                
                1. **Build**: Train or load model, run tests, build container
                2. **Test**: Validate model performance, run integration tests
                3. **Deploy**: Push to model registry, deploy to staging/production
                4. **Monitor**: Track model performance metrics
                
                Using GitHub Actions:
                
                ```yaml
                name: ML Model CI/CD
                
                on:
                  push:
                    branches: [ main ]
                  pull_request:
                    branches: [ main ]
                
                jobs:
                  build-and-test:
                    runs-on: ubuntu-latest
                    steps:
                      - uses: actions/checkout@v2
                      - name: Set up Python
                        uses: actions/setup-python@v2
                        with:
                          python-version: '3.9'
                      - name: Install dependencies
                        run: pip install -r requirements.txt
                      - name: Train model
                        run: python train_model.py
                      - name: Run tests
                        run: pytest
                      - name: Build Docker image
                        run: docker build -t ml-model:${{ github.sha }} .
                      
                  deploy:
                    needs: build-and-test
                    runs-on: ubuntu-latest
                    if: github.ref == 'refs/heads/main'
                    steps:
                      - name: Deploy to production
                        run: |
                          # Deployment steps
                          echo "Deploying model to production"
                ```
                
                ## Monitoring ML Models in Production
                
                Implement monitoring for:
                
                1. **Model Performance**: Accuracy, precision, recall
                2. **Data Drift**: Changes in input distribution
                3. **System Metrics**: Latency, throughput, resource usage
                
                ## Conclusion
                
                Successful ML model deployment requires a combination of software engineering best practices and ML-specific considerations. By containerizing models, implementing CI/CD pipelines, and establishing robust monitoring, you can ensure your models perform reliably in production.
                """,
                "created_at": "2025-04-28",
                "tags": [
                    {"name": "Machine Learning", "slug": "machine-learning"},
                    {"name": "DevOps", "slug": "devops"},
                    {"name": "Docker", "slug": "docker"},
                ],
            },
        ]

        # Find the post with matching slug
        post = next((p for p in posts if p["slug"] == slug), None)
        if not post:
            raise Http404(f"DataLog with slug '{slug}' does not exist")

        # Add related posts
        post["related_posts"] = [p for p in posts if p["id"] != post["id"]][:2]

        return post



# ================ START OLD VIEWS FOR REF ====================


# class PostListView(ListView):
#     """View for the blog homepage showing latest posts."""
#     model = DataLog
#     template_name = "blog/post_list.html"
#     context_object_name = "posts"
#     paginate_by = 6  # 6 posts per page (2 rows of 3)

#     def get_queryset(self):
#         return DataLog.objects.filter(
#             status="published").order_by("-published_date")

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['categories'] = Category.objects.all()
#         context['tags'] = Tag.objects.all()
#         context['featured_post'] = DataLog.objects.filter(
#             status='published',
#             featured=True
#             ).first()
#         return context


# class PostDetailView(DetailView):
#     """View for a single blog post."""
#     model = DataLog
#     template_name = "blog/post_detail.html"
#     context_object_name = "post"

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         post = self.get_object()

#         # Get related posts by tags
#         post_tags_ids = post.tags.values_list('id', flat=True)
#         related_posts = DataLog.objects.filter(
#             tags__in=post_tags_ids,
#             status='published'
#         ).exclude(id=post.id).distinct()[:3]

#         # Get previous and next posts
#         try:
#             previous_post = DataLog.objects.filter(
#                 published_date__lt=post.published_date,
#                 status='published'
#             ).order_by('-published_date').first()
#         except DataLog.DoesNotExist:
#             previous_post = None

#         try:
#             next_post = DataLog.objects.filter(
#                 published_date__gt=post.published_date,
#                 status='published'
#             ).order_by('published_date').first()
#         except DataLog.DoesNotExist:
#             next_post = None

#         # Get series information if applicable
#         series_post = SeriesLogEntry.objects.filter(post=post).first()
#         if series_post:
#             series = series_post.series
#             series_posts = SeriesLogEntry.objects.filter(series=series).order_by('order')

#             # Get next and previous posts in series
#             next_in_series = series_posts.filter(order__gt=series_post.order).first()
#             prev_in_series = series_posts.filter(order__lt=series_post.order).last()

#             context.update({
#                 'in_series': True,
#                 'series': series,
#                 'series_post': series_post,
#                 'next_in_series': next_in_series.post if next_in_series else None,
#                 'prev_in_series': prev_in_series.post if prev_in_series else None,
#                 'series_posts': [sp.post for sp in series_posts],
#             })

#         context.update({
#             'related_posts': related_posts,
#             'previous_post': previous_post,
#             'next_post': next_post,
#         })

#         # Extract headings for Table of Contents
#         headings = self.extract_headings(post.content)
#         context['headings'] = headings

#         return context

#     def extract_headings(self, markdown_content):
#         """Extract headings from markdown content for table of contents."""
#         headings = []
#         # Regular expression to find headings in markdown
#         heading_pattern = r'^(#{1,3})\s+(.+)$'

#         for line in markdown_content.split('\n'):
#             match = re.match(heading_pattern, line.strip())
#             if match:
#                 level = len(match.group(1))
#                 text = match.group(2).strip()
#                 # Create ID from heading text for anchor links
#                 # Using same splugify function as markdownify filter
#                 heading_id = slugify(text)
#                 headings.append({
#                     'level': level,
#                     'text': text,
#                     'id': heading_id
#                 })
#         return headings


# class CategoryView(ListView):
#     """View for posts filtered by category."""
#     model = DataLog
#     template_name = "blog/category.html"
#     context_object_name = "posts"
#     paginate_by = 6

#     def get_queryset(self):
#         self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
#         return DataLog.objects.filter(
#             category=self.category,
#             status="published").order_by('-published_date')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['category'] = self.category
#         # Add this line to track active category
#         context['category_slug'] = self.kwargs['slug']
#         return context


# class TagListView(ListView):
#     model = Tag
#     template_name = 'blog/tags.html'
#     context_object_name = 'tags'


# class TagView(ListView):
#     """View for posts filtered by tag."""
#     model = DataLog
#     template_name = "blog/tag.html"
#     context_object_name = "posts"
#     paginate_by = 6

#     def get_queryset(self):
#         self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
#         return DataLog.objects.filter(
#             tags=self.tag, status="published").order_by('-published_date')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['tag'] = self.tag

#         # Get related tags that appear together with this tag
#         tag_posts = DataLog.objects.filter(tags=self.tag)
#         related_tags = Tag.objects.filter(
#             posts__in=tag_posts
#         ).exclude(id=self.tag.id).annotate(
#             posts_count=Count('posts')
#         ).order_by('-posts_count')[:3]

#         context['related_tags'] = related_tags
#         return context


# class ArchiveView(ListView):
#     """View for archive page showing posts by year/month."""
#     template_name = "blog/archive.html"
#     context_object_name = 'posts'
#     paginate_by = 6

#     # Define the start date for timeline (April 2025)
#     start_year = 2024
#     start_month = 11

#     def get_queryset(self):
#         year = self.kwargs.get('year')
#         month = self.kwargs.get('month')

#         # If no year provided, show all posts
#         if not year:
#             return DataLog.objects.filter(
#                 status='published').order_by('-published_date')

#         # If month provided, filter by year and month
#         if month:
#             return DataLog.objects.filter(
#                 published_date__year=year,
#                 published_date__month=month,
#                 status='published'
#             ).order_by('-published_date')

#         # If only year provided, filter by year
#         return DataLog.objects.filter(
#             published_date__year=year,
#             status='published'
#         ).order_by('-published_date')

#     def get(self, request, *args, **kwargs):
#         # Current Date
#         current_date = datetime.now()
#         current_year = current_date.year
#         current_month = current_date.month

#         # Get year and month from kwargs
#         year = self.kwargs.get('year')
#         month = self.kwargs.get('month')

#         # Validate year and month
#         if year and (int(year) < self.start_year or int(year) > current_year):
#             return redirect('blog:archive')

#         if month and year and (
#             (int(year) == self.start_year and int(month) > self.start_month) or
#             (int(year) == current_year and int(month) > current_month) or
#             int(month) < 1 or int(month) > 12
#         ):
#             return redirect('blog:archive_year', year=year)

#         return super().get(request, *args, **kwargs)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         # Get current date info
#         current_date = datetime.now()
#         current_year = current_date.year
#         current_month = current_date.month

#         # Get year and month from kwargs
#         year = self.kwargs.get('year')
#         month = self.kwargs.get('month')

#         # Convert to integers if present
#         if year:
#             year = int(year)
#         if month:
#             month = int(month)
#             month_name = calendar.month_name[month]
#         else:
#             month_name = None

#         # Generate all years from start date to current date
#         years = list(range(self.start_year, current_year + 1))

#         # Generate all months for selected year
#         if year:
#             # For start year, only include months from start_month onward
#             if year == self.start_year:
#                 month_range = range(self.start_month, 13)
#             # For the current year, only include months up to current_month
#             elif year == current_year:
#                 month_range = range(1, current_month + 1)
#             # For other years, include all months
#             else:
#                 month_range = range(1, 13)

#             months = [(m, calendar.month_name[m]) for m in month_range]
#         else:
#             months = []

#         # Get post counts for each year/month if desired
#         year_counts = {}
#         for yr in years:
#             year_counts[yr] = DataLog.objects.filter(
#                 status='published',
#                 published_date__year=yr
#             ).count()

#         month_counts = {}
#         if year:
#             for m, _ in months:
#                 month_counts[m] = DataLog.objects.filter(
#                     status='published',
#                     published_date__year=year,
#                     published_date__month=m
#                 ).count()

#         # Add all context data
#         context.update({
#             'years': years,
#             'year': year,
#             'months': months,
#             'month': month,
#             'month_name': month_name,
#             'start_year': self.start_year,
#             'start_month': self.start_month,
#             'current_year': current_year,
#             'current_month': current_month,
#             'year_counts': year_counts,
#             'month_counts': month_counts,
#         })

#         return context


# class SearchView(ListView):
#     """View for search results."""
#     template_name = 'blog/search.html'
#     context_object_name = 'posts'
#     paginate_by = 6

#     def get_queryset(self):
#         query = self.request.GET.get('q')
#         if query:
#             return DataLog.objects.filter(
#                 title__icontains=query
#             ) | DataLog.objects.filter(
#                 content__icontains=query
#             ) | DataLog.objects.filter(
#                 tags__name__icontains=query
#             ).distinct().filter(
#                 status='published'
#             ).order_by('-published_date')
#         return DataLog.objects.none()

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['query'] = self.request.GET.get('q', '')
#         return context

# # ===================== ADMIN VIEWS FOR POST MANAGEMENT =====================


# class PostCreateView(LoginRequiredMixin, CreateView):
#     """View for creating new post."""

#     model = DataLog
#     form_class = PostForm
#     template_name = "blog/admin/post_form.html"

#     def get_success_url(self):
#         return reverse('blog:post_detail', kwargs={'slug': self.object.slug})

#     def form_valid(self, form):
#         # DEBUG: Print form data and POST Data
#         print("=" * 50)
#         print("FORM SUBMITTED")
#         print("POST Data:")
#         pprint.pprint(dict(self.request.POST))
#         print("Cleaned Data:")
#         pprint.pprint(form.cleaned_data)
#         print("=" * 50)

#         # Set the author to current user
#         form.instance.author = self.request.user

#         # Set publication date if status is published and no date
#         if form.instance.status == "published" and not form.instance.published_date:
#             form.instance.published_date = timezone.now()

#         # If no slug, generate from title
#         if not form.instance.slug:
#             form.instance.slug = slugify(form.instance.title)

#         # Add success message
#         messages.success(self.request, "DataLog created successfully!")
#         return super().form_valid(form)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["title"] = "Create New DataLog"
#         context["submit_text"] = "Create DataLog"
#         return context


# class PostUpdateView(LoginRequiredMixin, UpdateView):
#     """View for editing an existing blog post."""

#     model = DataLog
#     form_class = PostForm
#     template_name = "blog/admin/post_form.html"

#     def get_success_url(self):
#         return reverse("blog:post_detail", kwargs={"slug": self.object.slug})

#     def form_valid(self, form):
#         # DEBUG: Print the raw reuqest POST data and form cleaned_data
#         print("=" * 50)
#         print("FORM SUBMITTED")
#         print("POST Data:")
#         pprint.pprint(dict(self.request.POST))
#         print("Cleaned Data:")
#         pprint.pprint(form.cleaned_data)
#         print("Content Field BEFORE Save:")
#         print(form.instance.content)
#         print("=" * 50)

#         # Set publication date if status is published and doesn't have one
#         if form.instance.status == "published" and not form.instance.published_date:
#             form.instance.published_date = timezone.now()

#         # Save form and redirect & Add success message
#         response = super().form_valid(form)

#         # DEBUG AFTER SAVE
#         print("Content Field AFTER Save:")
#         print(self.object.content)
#         print("=" * 50)

#         messages.success(self.request, "DataLog updated successfully!")
#         return response

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["title"] = "Edit DataLog"
#         context["submit_text"] = "Update DataLog"

#         # Get series info
#         post = self.get_object()
#         series_post = SeriesLogEntry.objects.filter(post=post).first()
#         if series_post:
#             context["initial_series"] = series_post.series
#             context["initial_series_order"] = series_post.order

#         return context


# class PostDeleteView(LoginRequiredMixin, DeleteView):
#     """View for deleting logs post."""

#     model = DataLog
#     template_name = 'blog/admin/post_confirm_delete.html'
#     success_url = reverse_lazy('blog:dashboard')

#     def test_func(self):
#         """Only allows author or admin to delete post."""
#         post = self.get_object()
#         return self.request.user == post.author or self.request.user.is_superuser

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = 'Delete DataLog'
#         return context

#     def delete(self, request, *args, **kwargs):
#         messages.success(request, 'DataLog deleted successfully!')
#         return super().delete(request, *args, **kwargs)


# class CategoryCreateView(LoginRequiredMixin, CreateView):
#     """View for creating a new category."""

#     model = Category
#     form_class = CategoryForm
#     template_name = 'blog/admin/category_form.html'
#     success_url = reverse_lazy('blog:category_list')

#     def form_valid(self, form):
#         # Generate slug from name if not provided
#         if not form.instance.slug:
#             form.instance.slug = slugify(form.instance.name)

#         messages.success(self.request, 'Category created successfully!')
#         return super().form_valid(form)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = 'Create New Category'
#         context['submit_text'] = 'Create Category'
#         return context


# class CategoryUpdateView(LoginRequiredMixin, UpdateView):
#     """View for updating an existing category."""

#     model = Category
#     form_class = CategoryForm
#     template_name = 'blog/admin/category_form.html'
#     success_url = reverse_lazy('blog:category_list')

#     def form_valid(self, form):
#         messages.success(self.request, 'Category updated successfully!')
#         return super().form_valid(form)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = 'Edit Category'
#         context['submit_text'] = 'Update Category'
#         return context


# class CategoryListView(LoginRequiredMixin, ListView):
#     """View for listing all categories with post counts."""

#     model = Category
#     template_name = 'blog/admin/category_list.html'
#     context_object_name = 'categories'

#     def get_queryset(self):
#         return Category.objects.annotate(post_count=Count('posts')).order_by('name')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = 'Manage Categories'
#         return context


# class CategoryDeleteView(LoginRequiredMixin, DeleteView):
#     """View for deleting a category."""

#     model = Category
#     template_name = 'blog/admin/category_confirm_delete.html'
#     success_url = reverse_lazy('blog:category_list')

#     def test_func(self):
#         """Only allows superuser to delete categories."""
#         return self.request.user.is_superuser

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = 'Delete Category'

#         # Get posts that would be affected
#         affected_posts = DataLog.objects.filter(category=self.object)
#         context['affected_posts'] = affected_posts
#         context['affected_count'] = affected_posts.count()

#         return context

#     def delete(self, request, *args, **kwargs):
#         # Check if posts should be reassigned or deleted
#         if 'reassign' in request.POST:
#             new_category_id = request.POST.get('new_category')
#             if new_category_id:
#                 try:
#                     new_category = Category.objects.get(id=new_category_id)
#                     DataLog.objects.filter(category=self.get_object()).update(category=new_category)
#                     messages.success(request, f'DataLogs reassigned to {new_category.name}')
#                 except Category.DoesNotExist:
#                     messages.error(request, 'Selected category does not exist')
#                     return redirect(request.path)

#         messages.success(request, 'Category deleted successfully!')
#         return super().delete(request, *args, **kwargs)


# class DashboardView(LoginRequiredMixin, ListView):
#     """Dashboard view for logs management."""

#     model = DataLog
#     template_name = 'blog/admin/dashboard.html'
#     context_object_name = 'posts'

#     def get_queryset(self):
#         return DataLog.objects.all().order_by('-created')[:10]

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = 'DEVLOGs Dashboard'
#         context['post_count'] = DataLog.objects.count()
#         context['published_count'] = DataLog.objects.filter(status='published').count()
#         context['draft_count'] = DataLog.objects.filter(status='draft').count()
#         context['category_count'] = Category.objects.count()
#         context['tag_count'] = Tag.objects.count()
#         return context

# Keeping here bc I like this idea

# class TagSuggestionsView(View):
#     """Class-based view for getting tag suggestions."""

#     def get(self, request, *args, **kwargs):
#         query = request.GET.get("q", "").strip()
#         if query:
#             # Find matching tags
#             tags = Tag.objects.filter(name__icontains=query)[:10]
#             return JsonResponse(
#                 {"tags": [{"id": tag.id, "name": tag.name} for tag in tags]}
#             )
#         return JsonResponse({"tags": []})
