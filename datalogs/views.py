from django.views.generic import ListView, DetailView, DeleteView, CreateView, UpdateView
from django.views.generic.detail import SingleObjectMixin
# from django.views.generic.edit import CreateView, UpdateView
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse, HttpResponseRedirect
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
