from django.db import models
from django.utils.text import slugify
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify


class CorePage(models.Model):
    """Model for static pages like privacy policy, etc."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = MarkdownxField()
    meta_description = models.CharField(
        max_length=160,
        help_text="SEO meta description")
    is_published = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def rendered_content(self):
        """Return content as rendered HTML."""
        return markdownify(self.content)


class Skill(models.Model):
    """Dev skills with proficiency values for visualization."""

    CATEGORY_CHOICES = (
        ("languages", "Programming Languages"),
        ("frameworks", "Frameworks & Libraries"),
        ("tools", "Tools & Technologies"),
        ("databases", "Databases"),
        ("other", "Other Skills"),
    )

    name = models.CharField(max_length=50)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    proficiency = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)],
        help_text="Skill level from 1-5"
    )
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon name (e.g., fa-python)")
    color = models.CharField(max_length=7, default="#00f0ff", help_text="Hex color code")
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['category', 'display_order']

    def __str__(self):
        return self.name


class Education(models.Model):
    """Educational background."""

    institution = models.CharField(max_length=100)
    degree = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ["-end_date", "-start_date"]
        verbose_name_plural = "Education"

    def __str__(self):
        return f"{self.degree} from {self.institution}"


class Experience(models.Model):
    """Work experience."""

    company = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    technologies = models.CharField(max_length=200, blank=True, help_text="Comma-separated list of technologies used")

    class Meta:
        ordering = ["-end_date", "-start_date"]

    def __str__(self):
        return f"{self.position} at {self.company}"

    def get_technologies_list(self):
        """Return technologies as a list."""
        if self.technologies:
            return [tech.strip() for tech in self.technologies.split(",")]
        return []


class Contact(models.Model):
    """Model for contact form submissions."""

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.name} - {self.created_at.strftime('%Y-%m-%d')}"


class SocialLink(models.Model):
    """Model for social media and external profile links."""

    name = models.CharField(max_length=50)
    url = models.URLField()
    handle = models.CharField(max_length=100, blank=True)
    icon = models.CharField(
        max_length=50, blank=True, help_text="Font Awesome icon name (e.g., 'fa-github')"
    )
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.name
