from django.db import models
from django.utils.text import slugify


class Profile(models.Model):
    """Dev profile info."""
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=200, help_text="Your professional title")
    bio = models.TextField()
    headshot = models.ImageField(upload_to='profile/', null=True, blank=True)
    location = models.CharField(max_length=100)
    years_experience = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Skill(models.Model):
    """Dev skills with proficiency values for visualization."""
    CATEGORY_CHOICES = (
        ('languages', 'Programming Languages'),
        ('frameworks', 'Frameworks'),
        ('tools', 'Tools & Software'),
        ('data', 'Data Technologies'),
    )

    name = models.CharField(max_length=100)
    proficiency = models.PositiveIntegerField(help_text="Proficiency level (0-100)")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.CharField(max_length=255, blank=True)
    years = models.PositiveIntegerField(default=1, help_text="Years of experience")
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='skills')

    def __str__(self):
        return f"{self.name} ({self.proficiency}%)"


class Specialty(models.Model):
    """Technical specialties."""
    name = models.CharField(max_length=100)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='specialties')

    class Meta:
        verbose_name_plural = "Specialties"

    def __str__(self):
        return self.name


class FocusArea(models.Model):
    """Developer focus areas."""
    name = models.CharField(max_length=100)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='focus_areas')

    def __str__(self):
        return self.name


class Education(models.Model):
    """Educational background."""
    degree = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    year_start = models.PositiveIntegerField()
    year_end = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='education')

    class Meta:
        ordering = ['-year_end', '-year_start']

    def __str__(self):
        return f"{self.degree} at {self.institution}"


class Experience(models.Model):
    """Work experience."""
    position = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    year_start = models.PositiveIntegerField()
    year_end = models.PositiveIntegerField(null=True, blank=True)
    current = models.BooleanField(default=False)
    description = models.TextField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='experience')

    class Meta:
        ordering = ['-current', '-year_end', '-year_start']

    def __str__(self):
        return f"{self.position} at {self.company}"


class ContactMethod(models.Model):
    """Contact methods/social links."""
    name = models.CharField(max_length=50)
    url = models.URLField()
    handle = models.CharField(max_length=100, blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS class for icon (e.g., 'fa-github')")
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='contact_methods')

    def __str__(self):
        return self.name
