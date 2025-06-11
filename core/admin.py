from django.contrib import admin

from .models import CorePage, Skill, Education, Experience, Contact, SocialLink


@admin.register(CorePage)
class CorePageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "updated_at")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "content")
    list_filter = ("is_published",)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "proficiency", "display_order", "icon")
    list_filter = ("category", "proficiency")
    search_fields = ("name", "description")
    list_editable = ("proficiency", "display_order")


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = (
        "institution",
        "degree",
        "field_of_study",
        "start_date",
        "end_date",
        "is_current",
    )
    list_filter = ("is_current",)
    search_fields = ("institution", "degree", "field_of_study")


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("company", "position", "start_date", "end_date", "is_current")
    list_filter = ("is_current",)
    search_fields = ("company", "position", "description")


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at", "is_read")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("created_at",)

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    mark_as_read.short_description = "Mark selected messages as read"

    actions = ["mark_as_read"]


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "icon", "display_order")
    list_editable = ("display_order",)
    search_fields = ("name", "url")