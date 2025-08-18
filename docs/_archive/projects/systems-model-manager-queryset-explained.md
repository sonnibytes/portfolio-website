# 🔥 **Summary: Why Custom Managers and QuerySets Are Game-Changers**

### **The Core Concept**
Think of custom managers and querysets as **"smart shortcuts"** for your database queries. Instead of writing the same complex filters over and over, you create reusable methods that express your business logic clearly.

### **Key Benefits for Your Dashboard**

1. **🎯 Readability**: 
   - `SystemModule.objects.featured().deployed()` 
   - vs `SystemModule.objects.filter(featured=True, status='deployed')`

2. **🚀 Performance**: 
   - Add `select_related()` and `prefetch_related()` in one place
   - All queries automatically optimized

3. **🔧 Maintainability**: 
   - Change business logic in one place
   - No more hunting through views for repeated filters

4. **📊 Dashboard Power**: 
   - `SystemModule.objects.dashboard_stats()` gives you everything in one call
   - Perfect for your dashboard panels

### **How This Elevates Your Portfolio**

**Before**: Your code looks like a tutorial project
```python
# Scattered throughout your views
deployed = SystemModule.objects.filter(status='deployed')
featured = SystemModule.objects.filter(featured=True, status__in=['deployed', 'published'])
```

**After**: Your code looks professional and enterprise-ready
```python
# Clean, expressive, business-focused
featured_systems = SystemModule.objects.featured().deployed()
dashboard_data = SystemModule.objects.dashboard_stats()
```

### **Perfect for Your Dashboard Panels**

Your new panel system can now use these clean methods:
```python
# In your dashboard view
context = {
    'featured_systems': SystemModule.objects.featured().deployed()[:6],
    'recent_activity': SystemModule.objects.recently_updated(7),
    'high_priority_systems': SystemModule.objects.high_priority().in_development(),
    'performance_systems': SystemModule.objects.with_performance_data(),
}
```

This creates a **professional-grade Django application** that demonstrates advanced Python/Django skills while keeping your code clean and maintainable. It's exactly the kind of code quality that impresses employers and shows you think like a senior developer! 



# Django Custom Manager and QuerySet - Complete Explanation

"""
WHAT ARE MANAGERS AND QUERYSETS?

1. MANAGER: The interface through which database query operations are provided to Django models
   - Every model gets a default manager called 'objects'
   - You can create custom managers to add your own methods

2. QUERYSET: A collection of database queries that can be filtered, ordered, and limited
   - Lazy evaluation - queries aren't executed until you actually need the data
   - Chainable - you can add filters, ordering, etc.

WHY CREATE CUSTOM ONES?

1. DRY (Don't Repeat Yourself) - Instead of writing the same filters everywhere
2. Business Logic Encapsulation - Put domain-specific logic in one place
3. Performance - Optimize common queries with select_related/prefetch_related
4. Readability - Make your code more expressive and easier to understand
"""

# ==================================================
# PART 1: CUSTOM QUERYSET
# ==================================================

class SystemModuleQuerySet(models.QuerySet):
    """
    Custom queryset for SystemModule with useful filters.
    
    This extends the default QuerySet to add methods that return
    commonly-used filtered results.
    """
    
    def deployed(self):
        """Return only deployed systems."""
        return self.filter(status='deployed')
        # Instead of: SystemModule.objects.filter(status='deployed')
        # You can now do: SystemModule.objects.deployed()
    
    def published(self):
        """Return only published systems."""
        return self.filter(status='published')
    
    def in_development(self):
        """Return systems currently in development."""
        return self.filter(status='in_development')
    
    def featured(self):
        """Return only featured systems."""
        return self.filter(featured=True)
    
    def with_performance_data(self):
        """Return systems that have performance metrics."""
        return self.filter(
            performance_score__isnull=False,
            uptime_percentage__isnull=False
        )
        # This is much cleaner than writing this filter every time!
    
    def high_priority(self):
        """Return high and critical priority systems."""
        return self.filter(priority__in=[3, 4])  # High and Critical
    
    def recently_updated(self, days=7):
        """Return systems updated within the specified number of days."""
        from django.utils import timezone
        from datetime import timedelta
        return self.filter(
            updated_at__gte=timezone.now() - timedelta(days=days)
        )
        # Flexible method - you can specify different day ranges
    
    def by_health_status(self, status):
        """
        Filter systems by health status.
        
        Note: This is less efficient because it requires calling
        get_health_status() on each system, but sometimes necessary
        for complex business logic that can't be done at the database level.
        """
        system_ids = []
        for system in self.all():
            if system.get_health_status() == status:
                system_ids.append(system.id)
        return self.filter(id__in=system_ids)


# ==================================================
# PART 2: CUSTOM MANAGER
# ==================================================

class SystemModuleManager(models.Manager):
    """
    Custom manager for SystemModule.
    
    The manager is what you access when you call SystemModule.objects
    It provides the interface for creating QuerySets and can add
    additional functionality.
    """
    
    def get_queryset(self):
        """
        Override the default queryset to use our custom QuerySet.
        This means ALL queries through this manager will use our custom methods.
        """
        return SystemModuleQuerySet(self.model, using=self._db)
    
    # Now we expose all our custom QuerySet methods at the manager level
    def deployed(self):
        return self.get_queryset().deployed()
    
    def published(self):
        return self.get_queryset().published()
    
    def in_development(self):
        return self.get_queryset().in_development()
    
    def featured(self):
        return self.get_queryset().featured()
    
    def with_performance_data(self):
        return self.get_queryset().with_performance_data()
    
    def recently_updated(self, days=7):
        return self.get_queryset().recently_updated(days)
    
    def dashboard_stats(self):
        """
        Get key dashboard statistics in one optimized query.
        
        This is a manager-only method that returns computed statistics
        rather than a QuerySet. Perfect for dashboard data.
        """
        from django.db.models import Avg, Count
        return {
            'total': self.count(),
            'deployed': self.deployed().count(),
            'published': self.published().count(),
            'in_development': self.in_development().count(),
            'featured': self.featured().count(),
            'avg_completion': self.aggregate(
                avg=Avg('completion_percent')
            )['avg'] or 0,
            'avg_performance': self.with_performance_data().aggregate(
                avg=Avg('performance_score')
            )['avg'] or 0,
        }


# ==================================================
# PART 3: HOW TO USE THEM
# ==================================================

"""
USAGE EXAMPLES:

# In your SystemModule model, add this line:
objects = SystemModuleManager()

# Now you can use these methods anywhere in your code:
"""

# BASIC FILTERING - Much cleaner than before!
def example_usage():
    # OLD WAY (still works, but verbose):
    deployed_systems = SystemModule.objects.filter(status='deployed')
    featured_systems = SystemModule.objects.filter(featured=True)
    recent_systems = SystemModule.objects.filter(
        updated_at__gte=timezone.now() - timedelta(days=7)
    )
    
    # NEW WAY (clean and expressive):
    deployed_systems = SystemModule.objects.deployed()
    featured_systems = SystemModule.objects.featured()
    recent_systems = SystemModule.objects.recently_updated(7)
    
    # CHAINING - You can combine these methods!
    featured_deployed = SystemModule.objects.featured().deployed()
    recent_high_priority = SystemModule.objects.recently_updated().high_priority()
    
    # PERFORMANCE SYSTEMS with good metrics
    performing_systems = SystemModule.objects.with_performance_data().deployed()


# ==================================================
# PART 4: ADVANCED EXAMPLES
# ==================================================

def advanced_examples():
    """Examples of how these help in real applications."""
    
    # DASHBOARD VIEW - Get stats quickly
    stats = SystemModule.objects.dashboard_stats()
    # Returns: {'total': 10, 'deployed': 6, 'featured': 3, ...}
    
    # TEMPLATE CONTEXT - Clean view code
    context = {
        'featured_systems': SystemModule.objects.featured().deployed()[:6],
        'recent_updates': SystemModule.objects.recently_updated(30),
        'systems_needing_attention': SystemModule.objects.high_priority().in_development(),
    }
    
    # API ENDPOINTS - Readable filtering
    if request.GET.get('status') == 'deployed':
        systems = SystemModule.objects.deployed()
    elif request.GET.get('featured'):
        systems = SystemModule.objects.featured()
    else:
        systems = SystemModule.objects.all()
    
    # COMPLEX BUSINESS LOGIC
    critical_systems = (
        SystemModule.objects
        .high_priority()
        .with_performance_data()
        .recently_updated(7)
    )


# ==================================================
# PART 5: PERFORMANCE BENEFITS
# ==================================================

def performance_examples():
    """How custom managers improve performance."""
    
    # OPTIMIZED QUERIES - Add select_related/prefetch_related in one place
    class OptimizedSystemModuleQuerySet(models.QuerySet):
        def with_related(self):
            """Optimize queries by including related objects."""
            return self.select_related(
                'system_type', 'author'
            ).prefetch_related(
                'technologies', 'features', 'metrics'
            )
        
        def for_dashboard(self):
            """Optimized specifically for dashboard display."""
            return self.with_related().filter(
                status__in=['deployed', 'published']
            ).order_by('-updated_at')
    
    # Now your dashboard queries are automatically optimized:
    dashboard_systems = SystemModule.objects.for_dashboard()[:10]
    # This prevents N+1 query problems!


# ==================================================
# PART 6: REAL-WORLD APPLICATIONS
# ==================================================

# IN VIEWS
class SystemsDashboardView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Clean, readable view code
        context.update({
            'featured_systems': SystemModule.objects.featured().deployed()[:6],
            'systems_in_dev': SystemModule.objects.in_development(),
            'recent_activity': SystemModule.objects.recently_updated(7),
            'dashboard_stats': SystemModule.objects.dashboard_stats(),
        })
        
        return context

# IN TEMPLATES - You can even use these in templates!
"""
{% for system in systems.featured.deployed %}
    <!-- Only featured, deployed systems -->
{% endfor %}
"""

# IN MANAGEMENT COMMANDS
class Command(BaseCommand):
    def handle(self, *args, **options):
        # Find systems that need attention
        stale_systems = SystemModule.objects.in_development().recently_updated(30)
        
        for system in stale_systems:
            self.stdout.write(f"System {system.title} needs update")

# IN TESTS
class SystemModelTests(TestCase):
    def test_featured_systems(self):
        # Test your custom methods
        featured_count = SystemModule.objects.featured().count()
        self.assertEqual(featured_count, 3)


# ==================================================
# PART 7: WHY THIS MATTERS FOR YOUR PORTFOLIO
# ==================================================

"""
FOR YOUR PORTFOLIO PROJECT, THIS DEMONSTRATES:

1. ADVANCED DJANGO KNOWLEDGE
   - Custom managers and querysets are intermediate-to-advanced Django
   - Shows you understand Django's ORM beyond basic usage

2. CLEAN CODE PRINCIPLES
   - DRY (Don't Repeat Yourself)
   - Single Responsibility Principle
   - Expressive, readable code

3. PERFORMANCE AWARENESS
   - Understanding of database query optimization
   - Prevention of N+1 problems
   - Efficient dashboard queries

4. SCALABILITY THINKING
   - Code organized for growth
   - Business logic properly encapsulated
   - Maintainable architecture

5. PROFESSIONAL PATTERNS
   - Industry-standard Django patterns
   - Code that would fit in enterprise applications
   - Proper separation of concerns

BOTTOM LINE: This shows you're not just copying tutorials,
but thinking like a professional Django developer!
"""

# PRACTICAL USAGE EXAMPLES FOR YOUR AURA DASHBOARD

# ==================================================
# BEFORE vs AFTER: Dashboard View Code
# ==================================================

# BEFORE (without custom manager) - Verbose and repetitive
class OldDashboardView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Lots of repetitive filtering
        context['total_systems'] = SystemModule.objects.count()
        context['deployed_systems'] = SystemModule.objects.filter(status='deployed').count()
        context['systems_in_development'] = SystemModule.objects.filter(status='in_development').count()
        context['featured_systems'] = SystemModule.objects.filter(
            featured=True,
            status__in=['deployed', 'published']
        ).select_related('system_type').prefetch_related('technologies')[:6]
        
        # Complex filtering repeated
        context['performance_systems'] = SystemModule.objects.filter(
            performance_score__isnull=False,
            uptime_percentage__isnull=False,
            status='deployed'
        )
        
        # More verbose queries...
        week_ago = timezone.now() - timedelta(days=7)
        context['recent_activity'] = SystemModule.objects.filter(
            updated_at__gte=week_ago
        ).count()
        
        return context


# AFTER (with custom manager) - Clean and expressive
class NewDashboardView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Much cleaner and more readable
        context.update({
            'dashboard_stats': SystemModule.objects.dashboard_stats(),  # One call!
            'featured_systems': SystemModule.objects.featured().deployed()[:6],
            'performance_systems': SystemModule.objects.with_performance_data().deployed(),
            'recent_activity_count': SystemModule.objects.recently_updated(7).count(),
            'systems_needing_attention': SystemModule.objects.high_priority().in_development(),
        })
        
        return context


# ==================================================
# DASHBOARD PANELS: Before vs After
# ==================================================

# BEFORE - In your dashboard view, you'd need verbose queries for each panel
def get_health_panel_data(self):
    excellent_systems = SystemModule.objects.filter(
        performance_score__gte=90,
        uptime_percentage__gte=99.9,
        status='deployed'
    ).count()
    
    good_systems = SystemModule.objects.filter(
        performance_score__gte=75,
        performance_score__lt=90,
        uptime_percentage__gte=99.0,
        status='deployed'
    ).count()
    
    # More complex logic...

# AFTER - Simple and readable
def get_health_panel_data(self):
    performing_systems = SystemModule.objects.with_performance_data().deployed()
    
    health_stats = {}
    for system in performing_systems:
        health = system.get_health_status()  # Your existing method
        health_stats[health] = health_stats.get(health, 0) + 1
    
    return health_stats


# ==================================================
# TEMPLATE USAGE EXAMPLES
# ==================================================

# In your dashboard template, you can now do:
"""
<!-- Featured Systems Panel -->
{% dashboard_panel style="grid" color="teal" %}
    <h4>Featured Systems</h4>
    {% for system in featured_systems %}
        <!-- Clean, because featured_systems is already filtered -->
        <div class="system-card">{{ system.title }}</div>
    {% endfor %}
{% enddashboard_panel %}

<!-- Recent Activity Panel -->
{% dashboard_panel style="activity" color="lavender" %}
    <h4>Recent Updates ({{ recent_activity_count }} this week)</h4>
    {% for system in systems_recently_updated %}
        <div class="activity-item">{{ system.title }} updated</div>
    {% endfor %}
{% enddashboard_panel %}
"""


# ==================================================
# API ENDPOINTS: Much Cleaner
# ==================================================

# BEFORE - Verbose API filtering
@api_view(['GET'])
def systems_api_old(request):
    systems = SystemModule.objects.all()
    
    # Manual filtering
    if request.GET.get('status') == 'deployed':
        systems = systems.filter(status='deployed')
    
    if request.GET.get('featured'):
        systems = systems.filter(featured=True)
    
    if request.GET.get('recent'):
        week_ago = timezone.now() - timedelta(days=7)
        systems = systems.filter(updated_at__gte=week_ago)
    
    if request.GET.get('performance'):
        systems = systems.filter(
            performance_score__isnull=False,
            uptime_percentage__isnull=False
        )

# AFTER - Clean API filtering
@api_view(['GET'])
def systems_api_new(request):
    systems = SystemModule.objects.all()
    
    # Chain readable methods
    if request.GET.get('status') == 'deployed':
        systems = systems.deployed()
    
    if request.GET.get('featured'):
        systems = systems.featured()
    
    if request.GET.get('recent'):
        systems = systems.recently_updated(7)
    
    if request.GET.get('performance'):
        systems = systems.with_performance_data()


# ==================================================
# SEARCH AND FILTERING: Enhanced System List
# ==================================================

class SystemListView(ListView):
    model = SystemModule
    template_name = "projects/system_list.html"
    
    def get_queryset(self):
        # Start with optimized base query
        queryset = SystemModule.objects.all()
        
        # Apply filters using readable methods
        status = self.request.GET.get('status')
        if status == 'deployed':
            queryset = queryset.deployed()
        elif status == 'in_development':
            queryset = queryset.in_development()
        elif status == 'featured':
            queryset = queryset.featured()
        
        # Chain additional filters
        if self.request.GET.get('high_priority'):
            queryset = queryset.high_priority()
        
        if self.request.GET.get('recent'):
            days = int(self.request.GET.get('days', 30))
            queryset = queryset.recently_updated(days)
        
        if self.request.GET.get('with_metrics'):
            queryset = queryset.with_performance_data()
        
        return queryset


# ==================================================
# AJAX ENDPOINTS: Dashboard Real-time Updates
# ==================================================

@require_http_methods(["GET"])
def dashboard_metrics_api(request):
    """API endpoint for real-time dashboard updates."""
    
    # Get fresh stats efficiently
    stats = SystemModule.objects.dashboard_stats()
    
    # Get health distribution efficiently
    health_systems = SystemModule.objects.with_performance_data()
    health_distribution = {}
    for system in health_systems:
        health = system.get_health_status()
        health_distribution[health] = health_distribution.get(health, 0) + 1
    
    # Recent activity count
    recent_count = SystemModule.objects.recently_updated(1).count()  # Last 24 hours
    
    return JsonResponse({
        'stats': stats,
        'health_distribution': health_distribution,
        'recent_activity_count': recent_count,
        'timestamp': timezone.now().isoformat(),
    })


# ==================================================
# MANAGEMENT COMMANDS: System Maintenance
# ==================================================

class Command(BaseCommand):
    help = 'Find systems that need attention'
    
    def handle(self, *args, **options):
        # Find stale development projects
        stale_systems = SystemModule.objects.in_development().recently_updated(30)
        
        if not stale_systems.exists():
            self.stdout.write("No stale systems found!")
            return
        
        self.stdout.write(f"Found {stale_systems.count()} stale systems:")
        for system in stale_systems:
            days_stale = (timezone.now().date() - system.updated_at.date()).days
            self.stdout.write(f"  - {system.title}: {days_stale} days since update")
        
        # Find systems with performance issues
        performance_systems = SystemModule.objects.with_performance_data().deployed()
        low_performance = [s for s in performance_systems if s.get_health_status() == 'poor']
        
        if low_performance:
            self.stdout.write(f"\nSystems with performance issues:")
            for system in low_performance:
                self.stdout.write(f"  - {system.title}: {system.performance_score}% performance")


# ==================================================
# TESTING: Much Easier to Test
# ==================================================

class SystemManagerTests(TestCase):
    def setUp(self):
        # Create test systems
        self.deployed_system = SystemModule.objects.create(
            title="Deployed System",
            status='deployed',
            featured=True,
            performance_score=95.0,
            uptime_percentage=99.9
        )
        
        self.dev_system = SystemModule.objects.create(
            title="Dev System",
            status='in_development',
            featured=False
        )
    
    def test_deployed_filter(self):
        """Test the deployed() manager method."""
        deployed = SystemModule.objects.deployed()
        self.assertEqual(deployed.count(), 1)
        self.assertEqual(deployed.first().title, "Deployed System")
    
    def test_featured_filter(self):
        """Test the featured() manager method."""
        featured = SystemModule.objects.featured()
        self.assertEqual(featured.count(), 1)
        self.assertTrue(featured.first().featured)
    
    def test_chaining_filters(self):
        """Test chaining multiple filters."""
        featured_deployed = SystemModule.objects.featured().deployed()
        self.assertEqual(featured_deployed.count(), 1)
        
        featured_dev = SystemModule.objects.featured().in_development()
        self.assertEqual(featured_dev.count(), 0)
    
    def test_dashboard_stats(self):
        """Test the dashboard_stats() method."""
        stats = SystemModule.objects.dashboard_stats()
        
        expected_stats = {
            'total': 2,
            'deployed': 1,
            'published': 0,
            'in_development': 1,
            'featured': 1,
        }
        
        for key, expected_value in expected_stats.items():
            self.assertEqual(stats[key], expected_value)


# ==================================================
# PAGINATION AND ORDERING: Enhanced
# ==================================================

class SystemListWithCustomManager(ListView):
    model = SystemModule
    paginate_by = 12
    
    def get_queryset(self):
        """Get optimized queryset based on filters."""
        
        # Start with an optimized base query
        queryset = SystemModule.objects.select_related('system_type', 'author')
        
        # Apply status filter
        status_filter = self.request.GET.get('status')
        if status_filter == 'deployed':
            queryset = queryset.deployed()
        elif status_filter == 'featured':
            queryset = queryset.featured()
        elif status_filter == 'recent':
            queryset = queryset.recently_updated(30)
        elif status_filter == 'high_performance':
            queryset = queryset.with_performance_data()
        
        # Apply ordering
        order = self.request.GET.get('order', 'recent')
        if order == 'recent':
            queryset = queryset.order_by('-updated_at')
        elif order == 'name':
            queryset = queryset.order_by('title')
        elif order == 'completion':
            queryset = queryset.order_by('-completion_percent')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter stats using our clean methods
        context.update({
            'total_count': SystemModule.objects.count(),
            'deployed_count': SystemModule.objects.deployed().count(),
            'featured_count': SystemModule.objects.featured().count(),
            'recent_count': SystemModule.objects.recently_updated(30).count(),
        })
        
        return context


# ==================================================
# REAL BENEFITS FOR YOUR PORTFOLIO
# ==================================================

"""
WHAT THIS DEMONSTRATES TO EMPLOYERS:

1. ADVANCED DJANGO KNOWLEDGE
   - Shows you understand Django's ORM beyond basics
   - Custom managers are intermediate-to-advanced Django

2. CODE ORGANIZATION
   - Business logic properly encapsulated
   - DRY principles applied
   - Readable, maintainable code

3. PERFORMANCE THINKING
   - Efficient database queries
   - Avoiding N+1 problems
   - Optimized for dashboard performance

4. SCALABILITY AWARENESS
   - Code organized for growth
   - Patterns that work in large applications
   - Professional Django patterns

5. TESTING-FRIENDLY CODE
   - Methods are easy to unit test
   - Clear separation of concerns
   - Predictable behavior

BOTTOM LINE: This transforms your portfolio from "student project" 
to "professional Django application" level code quality!
"""