from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils import timezone
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
import re
from bs4 import BeautifulSoup


class Category(models.Model):
    """Category model for oraganizing datalogs."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    code = models.CharField(max_length=2,
                            help_text="Two-letter code for display in hexagon")
    description = models.TextField(blank=True)
    color = models.CharField(
        max_length=7, default="#00f0ff",
        help_text="Hex color code (e.g., #00f0ff)")
    icon = models.CharField(
        max_length=50, blank=True,
        help_text="Font Awesome icon name (e.g., fa-book-open)")

    class Meta:
        verbose_name_plural = "categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('datalogs:category', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)


class Tag(models.Model):
    """Tags for blog posts/data logs."""
    name = models.CharField(max_length=20)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('datalogs:tag', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Tag, self).save(*args, **kwargs)


class DataLog(models.Model):
    """Blog post model renamed to DataLog. (log{s} replace{s} post{s})"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    # Code format options
    CODE_FORMAT_CHOICES = (
        ("python", "Python"),
        ("javascript", "JavaScript"),
        ("html", "HTML"),
        ("css", "CSS"),
        ("terminal", "Terminal"),
        ("markdown", "Markdown"),
        ("json", "JSON"),
        ("sql", "SQL"),
        ("bash", "Bash/Shell"),
        ("plaintext", "Plain Text"),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    excerpt = models.TextField(
        blank=True, help_text="Short description for display in log cards")
    featured = models.BooleanField(
        default=False, help_text="Feature this log on the datalogs homepage")
    featured_code = models.TextField(
        blank=True, help_text="Code snippet to display in featured section")
    featured_code_format = models.CharField(
        max_length=20,
        choices=CODE_FORMAT_CHOICES,
        default='python',
        help_text="Programming language for syntax highlighting")
    show_toc = models.BooleanField(
        default=True, help_text="Show table of contents on log detail page")
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='draft')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(blank=True, null=True)
    reading_time = models.PositiveIntegerField(
        default=0, editable=False,
        help_text="Estimated reading time in minutes")
    content = MarkdownxField()
    # Relationship Fields
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="logs"
        )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True, related_name="logs"
        )
    tags = models.ManyToManyField(Tag, blank=True, related_name="logs")

    class Meta:
        ordering = ['-published_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('datalogs:datalog_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # If publishing for first time, set published_date
        if self.status == 'published' and not self.published_date:
            self.published_date == timezone.now()

        # Calculate reading time
        if self.content:
            # Avg reading speed: 200 words per minute
            word_count = len(re.findall(r'\w+', self.content))
            self.reading_time = max(1, round(word_count / 200))

        # Generate excerpt from content if not provided
        if not self.excerpt and self.content:
            # Strip markdown and get first 150 characters
            plain_text = re.sub(r'#|\*|\[|\]|\(|\)|_|`', '', self.content)
            self.excerpt = plain_text[:150] + '...' if len(plain_text) > 150 else plain_text

        super(DataLog, self).save(*args, **kwargs)

    def rendered_content(self):
        """Return content field as HTML with heading IDs for TOC links."""
        html_content = markdownify(self.content)
        soup = BeautifulSoup(html_content, 'html.parser')

        # Add IDs to headings
        for h in soup.find_all(['h2', 'h3', 'h4', 'h5', 'h6']):
            if not h.get('id'):
                h['id'] = slugify(h.get_text())

        return str(soup)

    def get_code_filename(self):
        """Return suitable filename for featured codeblock based on content."""
        # Map code formats to appropriate filenames
        format_to_filename = {
            'python': 'example.py',
            'javascript': 'script.js',
            'html': 'index.html',
            'css': 'styles.css',
            'terminal': 'terminal.sh',
            'markdown': 'readme.md',
            'json': 'data.json',
            'sql': 'query.sql',
            'bash': 'script.sh',
            'plaintext': 'file.txt',
        }
        # Return the appropriate filename based on format
        return format_to_filename.get(self.featured_code_format, 'code.txt')

    def get_headings(self):
        """Extract headings from markdown content for table of contents."""
        headings = []
        # Regular expression to find headings in markdown
        heading_pattern = r'^(#{1,3})\s+(.+)$'

        for line in self.content.split('\n'):
            match = re.match(heading_pattern, line.strip())
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()
                # Create an ID from heading text for anchor links
                heading_id = slugify(text)
                headings.append({
                    'level': level,
                    'text': text,
                    'id': heading_id,
                })

        return headings

    # Handle Series
    def is_in_series(self):
        """Check if log is part of a series."""
        return SeriesLogEntry.objects.filter(log=self).exists()

    def get_series(self):
        """Get the series this log entry belongs to, if any."""
        series_log = SeriesLogEntry.objects.filter(log=self).first()
        if series_log:
            return series_log.series
        return None

    def get_series_order(self):
        """Get the order of this log is in its series, if any."""
        series_log = SeriesLogEntry.objects.filter(log=self).first()
        if series_log:
            return series_log.order
        return None

    def get_similar_logs(self, count=3):
        """Get simimlar datalogs based on tags."""
        log_tags_ids = self.tags.values_list('id', flat=True)
        similar_logs = DataLog.objects.filter(
            tags__in=log_tags_ids,
            status='published'
        ).exclude(id=self.id).distinct()

        # Return datalogs ordered by number of matching tags
        return similar_logs.annotate(
            same_tags=models.Count('tags')
        ).order_by('-same_tags')[:count]


class Comment(models.Model):
    """Model for datalog comments."""
    log = models.ForeignKey(
        DataLog, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return f"Comment by {self.name} on {self.log}"


class Series(models.Model):
    """Model for creating datalogs series."""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Series"
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('datalogs:series', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Series, self).save(*args, **kwargs)


class SeriesLogEntry(models.Model):
    """Model for associating log entries with a series and ordering them."""
    series = models.ForeignKey(
        Series, on_delete=models.CASCADE, related_name='logs')
    log = models.ForeignKey(
        DataLog, on_delete=models.CASCADE, related_name='series_associations')
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ('series', 'log')

    def __str__(self):
        return f"{self.log} in {self.series} (#{self.order})"


class LogImage(models.Model):
    """Images for blog posts/data logs."""
    log = models.ForeignKey(DataLog, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='logs/')
    caption = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Image for {self.log.title}"


class LogMetric(models.Model):
    """Metrics for data log visualization."""
    log = models.ForeignKey(DataLog, on_delete=models.CASCADE, related_name='metrics')
    name = models.CharField(max_length=100)
    value = models.FloatField()

    def __str__(self):
        return f"{self.name}: {self.value} ({self.log.title})"
    