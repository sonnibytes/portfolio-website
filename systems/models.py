from django.db import models
from django.utils.text import slugify


class Technology(models.Model):
    """Technologies used in projects."""
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS class for icon (e.g., 'fa-python')")

    class Meta:
        verbose_name_plural = "Technologies"

    def __str__(self):
        return self.name
    

class Category(models.Model):
    """Project categories."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class System(models.Model):
    """Project/System model (formerly Project)."""
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
        ('experimental', 'Experimental'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    content = models.TextField()
    featured = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    completion_percentage = models.PositiveIntegerField(default=100)
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    technologies = models.ManyToManyField(Technology, through='SystemTechnology')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='systems')

    class Meta:
        ordering = ['-featured', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class SystemTechnology(models.Model):
    """Join model for Systems and Techonologies with percentage used."""
    system = models.ForeignKey(System, on_delete=models.CASCADE)
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE)
    percentage = models.PositiveIntegerField(default=0, help_text="Percentage of project using this tech")

    class Meta:
        verbose_name_plural = "System Technologies"

    def __str__(self):
        return f"{self.technology.name} ({self.percentage}%) in {self.system.title}"


class SystemImage(models.Model):
    """Images for projects/systems."""
    system = models.ForeignKey(System, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='systems/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.system.title}"


class SystemMetric(models.Model):
    """Performance metrics for projects/systems."""
    system = models.ForeignKey(System, on_delete=models.CASCADE, related_name='metrics')
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    description = models.CharField(max_length=225, blank=True)

    def __str__(self):
        return f"{self.system}: {self.value} ({self.system.title})"
