# blog/management/commands/test_datalog_features.py
"""
Management command to test DataLog features and optionally create sample data
Usage: python manage.py test_datalog_features [--create-samples]
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from blog.models import Post, Category, Tag
from blog.templatetags.datalog_tags import *
from core.templatetags.aura_filters import *
import random

User = get_user_model()


class Command(BaseCommand):
    help = "Test DataLog features and optionally create sample data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--create-samples",
            action="store_true",
            help="Create sample posts, categories, and tags for testing",
        )
        parser.add_argument(
            "--test-functions",
            action="store_true",
            help="Test all template tag functions",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🧪 Testing DataLog Features\n"))

        # Always run basic tests
        self.test_template_tags()

        if options["test_functions"]:
            self.test_individual_functions()

        if options["create_samples"]:
            self.create_sample_data()

        self.stdout.write(self.style.SUCCESS("\n✅ DataLog features test completed!"))

    def test_template_tags(self):
        """Test basic template tag functionality"""
        self.stdout.write("📊 Testing template tags...")

        try:
            # Test datalog_stats
            stats = datalog_stats()
            self.stdout.write(
                f"  ✓ Stats: {stats['total_posts']} posts, {stats['total_categories']} categories"
            )

            # Test recent activity
            activity = recent_datalog_activity(30)
            self.stdout.write(
                f"  ✓ Recent activity: {activity['count']} posts in last 30 days"
            )

            # Test popular categories
            categories = get_datalog_categories()
            self.stdout.write(f"  ✓ All Categories: {len(categories)} found")

            # Test search suggestions
            suggestions = datalog_search_suggestions("python")
            self.stdout.write(
                f"  ✓ Search suggestions: {len(suggestions)} for 'python'"
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Template tag error: {str(e)}"))

    def test_individual_functions(self):
        """Test individual filter and tag functions"""
        self.stdout.write("\n🔧 Testing individual functions...")

        # Test code analysis functions
        sample_code = """
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

# Generate first 10 fibonacci numbers
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
"""

        try:
            line_count = code_line_count(sample_code)
            complexity = code_complexity(sample_code)
            self.stdout.write(
                f"  ✓ Code analysis: {line_count} lines, {complexity} complexity"
            )

            # Test reading progress colors
            colors = [
                get_reading_progress_color(3),
                get_reading_progress_color(10),
                get_reading_progress_color(20),
            ]
            self.stdout.write(
                f"  ✓ Reading colors: {len(colors)} color values generated"
            )

            # Test file size formatting
            sizes = [
                file_size(1024),
                file_size(1048576),
                file_size(1073741824),
            ]
            self.stdout.write(f"  ✓ File sizes: {', '.join(sizes)}")

            # Test string splitting
            tags = split_string("python,django,web-development")
            self.stdout.write(
                f"  ✓ String split: {len(tags)} tags from comma-separated string"
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Function test error: {str(e)}"))

    def create_sample_data(self):
        """Create sample data for testing"""
        self.stdout.write("\n📝 Creating sample data...")

        try:
            # Get or create a user
            user, created_at = User.objects.get_or_create(
                username="testuser",
                defaults={
                    "email": "test@example.com",
                    "first_name": "Test",
                    "last_name": "User",
                },
            )

            # Create sample categories
            categories_data = [
                {"name": "Machine Learning", "code": "ML", "color": "#b39ddb"},
                {"name": "Web Development", "code": "WEB", "color": "#26c6da"},
                {"name": "Data Science", "code": "DATA", "color": "#ff8a80"},
                {"name": "System Design", "code": "SYS", "color": "#a5d6a7"},
                {"name": "DevOps", "code": "OPS", "color": "#fff59d"},
            ]

            categories = []
            for cat_data in categories_data:
                category, created_at = Category.objects.get_or_create(
                    name=cat_data["name"],
                    defaults={
                        "code": cat_data["code"],
                        "color": cat_data["color"],
                        "slug": cat_data["name"].lower().replace(" ", "-"),
                    },
                )
                categories.append(category)
                if created_at:
                    self.stdout.write(f"  ✓ Created category: {category.name}")

            # Create sample tags
            tag_names = [
                "python",
                "django",
                "javascript",
                "react",
                "machine-learning",
                "neural-networks",
                "data-analysis",
                "api-development",
                "docker",
                "kubernetes",
                "postgresql",
                "redis",
                "aws",
                "tensorflow",
            ]

            tags = []
            for tag_name in tag_names:
                tag, created_at = Tag.objects.get_or_create(
                    name=tag_name, defaults={"slug": tag_name}
                )
                tags.append(tag)
                if created_at:
                    self.stdout.write(f"  ✓ Created tag: {tag.name}")

            # Create sample posts
            sample_posts = [
                {
                    "title": "Building Neural Networks with Python",
                    "excerpt": "A comprehensive guide to building neural networks from scratch using Python and NumPy.",
                    "content": """# Building Neural Networks with Python

## Introduction
Neural networks are the foundation of modern machine learning. In this post, we'll build one from scratch.

## Implementation
Let's start with the basic structure...

## Code Example
```python
import numpy as np

class NeuralNetwork:
    def __init__(self, layers):
        self.layers = layers
        self.weights = []
        self.biases = []
        
    def forward(self, x):
        # Forward propagation logic
        pass
```

## Conclusion
Building neural networks from scratch helps understand the fundamentals.
""",
                    "featured_code": """import numpy as np

class NeuralNetwork:
    def __init__(self, layers):
        self.layers = layers
        self.weights = []
        self.biases = []
        
        # Initialize weights and biases
        for i in range(len(layers) - 1):
            w = np.random.randn(layers[i], layers[i+1]) * 0.01
            b = np.zeros((1, layers[i+1]))
            self.weights.append(w)
            self.biases.append(b)
    
    def sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -250, 250)))
    
    def forward(self, x):
        self.activations = [x]
        
        for i in range(len(self.weights)):
            z = np.dot(self.activations[-1], self.weights[i]) + self.biases[i]
            a = self.sigmoid(z)
            self.activations.append(a)
        
        return self.activations[-1]""",
                    "featured_code_format": "python",
                    "category": categories[0],  # ML category
                    "reading_time": 12,
                    "featured": True,
                },
                {
                    "title": "Django REST API Best Practices",
                    "excerpt": "Learn the best practices for building scalable REST APIs with Django REST Framework.",
                    "content": """# Django REST API Best Practices

## Authentication and Permissions
Securing your API is crucial...

## Serialization Strategies
Effective data serialization...

## Performance Optimization
Tips for fast APIs...
""",
                    "featured_code": """from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        user = self.get_object()
        # Password change logic here
        return Response({'status': 'password changed'})""",
                    "featured_code_format": "python",
                    "category": categories[1],  # Web Dev category
                    "reading_time": 8,
                },
                {
                    "title": "Data Visualization with Python",
                    "excerpt": "Creating beautiful and informative data visualizations using matplotlib and seaborn.",
                    "content": """# Data Visualization with Python

## Getting Started
Data visualization is essential for understanding patterns...

## Matplotlib Basics
The foundation of Python plotting...

## Advanced Seaborn Techniques
Statistical visualizations made easy...
""",
                    "featured_code": """import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Create sample data
np.random.seed(42)
data = pd.DataFrame({
    'x': np.random.randn(100),
    'y': np.random.randn(100),
    'category': np.random.choice(['A', 'B', 'C'], 100)
})

# Create a beautiful visualization
plt.figure(figsize=(12, 8))

# Subplot 1: Scatter plot
plt.subplot(2, 2, 1)
sns.scatterplot(data=data, x='x', y='y', hue='category', alpha=0.7)
plt.title('Scatter Plot by Category')

# Subplot 2: Distribution
plt.subplot(2, 2, 2)
sns.histplot(data=data, x='x', kde=True, alpha=0.7)
plt.title('Distribution of X')

# Subplot 3: Box plot
plt.subplot(2, 2, 3)
sns.boxplot(data=data, x='category', y='y')
plt.title('Y Values by Category')

# Subplot 4: Correlation heatmap
plt.subplot(2, 2, 4)
corr_data = data[['x', 'y']].corr()
sns.heatmap(corr_data, annot=True, cmap='coolwarm', center=0)
plt.title('Correlation Matrix')

plt.tight_layout()
plt.show()""",
                    "featured_code_format": "python",
                    "category": categories[2],  # Data Science category
                    "reading_time": 15,
                },
            ]

            # Create the posts
            created_posts = 0
            for post_data in sample_posts:
                # Check if post already exists
                if not Post.objects.filter(title=post_data["title"]).exists():
                    post = Post.objects.create(
                        title=post_data["title"],
                        slug=post_data["title"].lower().replace(" ", "-"),
                        excerpt=post_data["excerpt"],
                        content=post_data["content"],
                        featured_code=post_data.get("featured_code", ""),
                        featured_code_format=post_data.get(
                            "featured_code_format", "python"
                        ),
                        author=user,
                        category=post_data["category"],
                        status="published",
                        reading_time=post_data.get("reading_time", 5),
                        featured=post_data.get("featured", False),
                    )

                    # Add some random tags
                    post_tags = random.sample(tags, random.randint(2, 5))
                    post.tags.set(post_tags)

                    created_posts += 1
                    self.stdout.write(f"  ✓ Created post: {post.title}")

            self.stdout.write(f"\n📊 Sample data created:")
            self.stdout.write(f"  • {len(categories)} categories")
            self.stdout.write(f"  • {len(tags)} tags")
            self.stdout.write(f"  • {created_posts} new posts")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"  ❌ Sample data creation error: {str(e)}")
            )

    def test_code_highlighting(self):
        """Test Pygments code highlighting"""
        self.stdout.write("\n💻 Testing code highlighting...")

        sample_code = (
            "print('Hello, AURA!')\nfor i in range(5):\n    print(f'Count: {i}')"
        )

        try:
            highlighted = highlight_code(sample_code, "python")
            css = pygments_css()

            if highlighted and css:
                self.stdout.write("  ✓ Pygments highlighting working")
            else:
                self.stdout.write(
                    self.style.WARNING("  ⚠️ Pygments highlighting may have issues")
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"  ❌ Code highlighting error: {str(e)}")
            )
