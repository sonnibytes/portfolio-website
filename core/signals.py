from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from blog.models import Tag
from core.models import Skill
from projects.models import Technology


@receiver(post_save, sender=Skill)
def create_skill_tag(sender, instance, created, **kwargs):
    """
    Automatically create a Tag when a new Skill is created.
    Tag name format: skill name (e.g., "Data Visualization", "Django ORM")
    """
    # Only on creation, not updates
    if created:
        tag_name = instance.name.lower()
        tag_slug = slugify(tag_name)

        # Check if Tag already exists (avoid dupes)
        if not Tag.objects.filter(slug=tag_slug).exists():
            Tag.objects.create(
                name=tag_name,
                slug=tag_slug
            )
            print(f"Auto-created tah '{tag_name}' from Skill")


@receiver(post_save, sender=Technology)
def create_technology_tag(sender, instance, created, **kwargs):
    """
    Automatically create a Tag when a new Technology is created.
    Tag name format: technology name (e.g., "PostgreSQL", "Chart.js")
    """
    # Only on creation, not updates
    if created:
        tag_name = instance.name.lower()
        tag_slug = slugify(tag_name)

        # Checkc if tag already exists (avoid dupes)
        if not Tag.objects.filter(slug=tag_slug).exists():
            Tag.objects.create(
                name=tag_name,
                slug=tag_slug
            )
            print(f"Auto-created tag '{tag_name}' from Technology")
