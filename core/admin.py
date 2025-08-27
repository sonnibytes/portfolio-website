from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import CorePage, Skill, Education, Experience, Contact, SocialLink, PortfolioAnalytics, SkillTechnologyRelation


# ========== NEW: SKILL-TECHNOLOGY RELATIONSHIP MANAGEMENT ==========

class SkillTechnologyRelationInline(admin.TabularInline):
    """Inline editing of skill-technology relationships with Skill admin"""
    model = SkillTechnologyRelation
    extra = 1
    fields = ['technology', 'strength', 'relationship_type', 'notes']
    autocomplete_fields = ['technology']
    verbose_name = "Related Technology"
    verbose_name_plural = "Related Technologies"


@admin.register(SkillTechnologyRelation)
class SkillTechnologyRelationAdmin(admin.ModelAdmin):
    """Standalone management of skill-technology relationships"""
    list_display = ['skill', 'technology', 'strength_display', 'relationship_type', 'strength_color']
    list_filter = ['strength', 'relationship_type', 'skill__category']
    search_fields = ['skill__name', 'technology__name', 'notes']
    autocomplete_fields = ['skill', 'technology']
    list_select_related = ['skill', 'technology']

    fieldsets = (
        ('Relationship', {
            'fields': ('skill', 'technology', 'strength', 'relationship_type')
        }),
        ('Context & Notes', {
            'fields': ('notes', 'first_used_together', 'last_used_together'),
            'classes': ('collapse',)
        }),
    )

    def strength_display(self, obj):
        return obj.get_strength_display()
    strength_display.short_description = "Strength"

    def strength_color(self, obj):
        color = obj.get_strength_color()
        return format_html(
            '<span style="color: {}; font-size: 16px;">●</span>', 
            color
        )
    strength_color.short_description = "Level"


@admin.register(PortfolioAnalytics)
class PortfolioAnalyticsAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "unique_visitors",
        "page_views",
        "engagement_display",
        "conversion_display",
        "top_content_display",
    )
    list_filter = ("date", "top_country", "organic_search_percentage")
    search_fields = ("date", "top_country", "top_city", "top_referrer")
    readonly_fields = ("engagement_score", "conversion_rate")
    date_hierarchy = "date"
    ordering = ("-date",)

    fieldsets = (
        ("Date & Location", {"fields": ("date", "top_country", "top_city")}),
        (
            "Visitor Metrics",
            {
                "fields": (
                    "unique_visitors",
                    "page_views",
                    "bounce_rate",
                    "avg_session_duration",
                )
            },
        ),
        (
            "Content Engagement",
            {
                "fields": (
                    "datalog_views",
                    "system_views",
                    "contact_form_submissions",
                    "github_clicks",
                )
            },
        ),
        ("Top Performing Content", {"fields": ("top_datalog", "top_system")}),
        ("Traffic Sources", {"fields": ("top_referrer", "organic_search_percentage")}),
        (
            "Calculated Metrics",
            {
                "fields": ("engagement_score", "conversion_rate"),
                "classes": ("collapse",),
            },
        ),
    )

    def engagement_display(self, obj):
        score = obj.engagement_score()
        if score >= 75:
            color = "#27c93f"
        elif score >= 50:
            color = "#ffbd2e"
        else:
            color = "#ff8a80"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}/100</span>', color, score
        )

    engagement_display.short_description = "Engagement"

    def conversion_display(self, obj):
        rate = obj.conversion_rate()
        return format_html("{:.1f}%", rate)

    conversion_display.short_description = "Conversion Rate"

    def top_content_display(self, obj):
        content = []
        if obj.top_datalog:
            content.append(f"📝 {obj.top_datalog.title[:30]}...")
        if obj.top_system:
            content.append(f"⚙️ {obj.top_system.title[:30]}...")
        return format_html("<br>".join(content)) if content else "-"

    top_content_display.short_description = "Top Content"


@admin.register(CorePage)
class CorePageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "created_at", "updated_at")
    list_filter = ("is_published", "created_at")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")


# ========== UPDATED: SKILL ADMIN ==========

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """Enhanced Skill admin w technology relationships"""
    list_display = (
        "name",
        "category",
        "proficiency_stars",
        "experience_level",
        "technology_count",
        "featured_status",
        "recency_status",
        "display_order",
        "is_featured",
    )

    list_filter = (
        "category",
        "proficiency",
        "is_featured",
        "is_currently_learning",
        "is_certified",
    )
    search_fields = ("name", "description")
    list_editable = ("display_order", "is_featured")
    prepopulated_fields = {"slug": ("name",)}

    # Add inline for tech relationships
    inlines = [SkillTechnologyRelationInline]

    fieldsets = (
        ("Basic Information", {"fields": ("name", "slug", "category", "description")}),
        (
            "Proficiency & Experience",
            {
                "fields": (
                    "proficiency",
                    "years_experience",
                    "last_used",
                    "is_currently_learning",
                    "is_certified",
                )
            },
        ),
        (
            "Visual & Display",
            {"fields": ("icon", "color", "display_order", "is_featured")},
        ),
    )

    def proficiency_stars(self, obj):
        stars = "★" * obj.proficiency + "☆" * (5 - obj.proficiency)
        return format_html('<span style="color: #ffbd2e;">{}</span>', stars)

    proficiency_stars.short_description = "Proficiency"

    def experience_level(self, obj):
        level = obj.get_experience_level()
        colors = {
            "Expert": "#27c93f",
            "Advanced": "#00f0ff",
            "Intermediate": "#ffbd2e",
            "Beginner": "#ff8a80",
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(level, "#808080"),
            level,
        )

    experience_level.short_description = "Experience"

    # Updated function for new many-to-many relationship
    def technology_count(self, obj):
        """Show count of related technologies"""
        count = obj.related_technologies.count()
        if count > 0:
            return format_html(
                '<span style="color: #00f0ff; font-weight: bold;">{} tech{}</span>',
                count,
                's' if count != 1 else ''
            )
        return format_html('<span style="color: #999;">No tech</span>')

    technology_count.short_description = "Technologies"

    def featured_status(self, obj):
        if obj.is_featured:
            return format_html('<span style="color: #27c93f;">⭐ Featured</span>')
        return "-"

    featured_status.short_description = "Featured"

    def recency_status(self, obj):
        if obj.is_recent():
            return format_html('<span style="color: #27c93f;">✓ Recent</span>')
        else:
            return format_html('<span style="color: #ff8a80;">⚠ Outdated</span>')

    recency_status.short_description = "Recency"


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
    list_filter = ("is_current", "start_date", "end_date")
    search_fields = ("institution", "degree", "field_of_study")
    prepopulated_fields = {"slug": ("institution",)}


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("company", "position", "start_date", "end_date", "is_current")
    list_filter = ("is_current", "start_date", "end_date")
    search_fields = ("company", "position", "description", "technologies")
    prepopulated_fields = {"slug": ("company",)}


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "inquiry_category",
        "priority_display",
        "response_status",
        "created_at",
        "response_time_display",
    )
    list_filter = (
        "inquiry_category",
        "priority",
        "response_sent",
        "created_at",
        "is_read",
    )
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("created_at", "response_time_hours", "ip_address")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    actions = ["mark_as_responded", "mark_as_high_priority"]

    fieldsets = (
        ("Contact Information", {"fields": ("name", "email", "subject")}),
        ("Message Content", {"fields": ("message", "inquiry_category", "priority")}),
        (
            "Response Tracking",
            {
                "fields": (
                    "is_read",
                    "response_sent",
                    "response_date",
                    "response_time_hours",
                )
            },
        ),
        (
            "Metadata",
            {
                "fields": ("referrer_page", "user_agent", "ip_address", "created_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def priority_display(self, obj):
        colors = {
            "urgent": "#f44336",
            "high": "#ff8a80",
            "normal": "#ffbd2e",
            "low": "#808080",
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.priority, "#808080"),
            obj.get_priority_display(),
        )

    priority_display.short_description = "Priority"

    def response_status(self, obj):
        if obj.response_sent:
            return format_html('<span style="color: #27c93f;">✓ Responded</span>')
        else:
            return format_html('<span style="color: #ff8a80;">⏳ Pending</span>')

    response_status.short_description = "Status"

    def response_time_display(self, obj):
        hours = obj.response_time_hours()
        if hours:
            if hours <= 24:
                color = "#27c93f"
            elif hours <= 72:
                color = "#ffbd2e"
            else:
                color = "#ff8a80"
            formatted_hours = "{:.1f}".format(hours)
            return format_html('<span style="color: {};">{}h</span>', color, formatted_hours)
        return "-"

    response_time_display.short_description = "Response Time"

    def mark_as_responded(self, request, queryset):
        for contact in queryset:
            contact.mark_as_responded()
        self.message_user(request, f"Marked {queryset.count()} contacts as responded.")

    mark_as_responded.short_description = "Mark selected as responded"

    def mark_as_high_priority(self, request, queryset):
        queryset.update(priority="high")
        self.message_user(request, f"Set {queryset.count()} contacts to high priority.")

    mark_as_high_priority.short_description = "Set to high priority"


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "handle", "display_order", "category")
    search_fields = ("name", "handle", "url", "category")
    list_editable = ("display_order",)
    ordering = ("display_order", "name")


# Customize admin site
admin.site.site_header = "AURA Portfolio Administration"
admin.site.site_title = "AURA Admin"
admin.site.index_title = "Portfolio Control Panel"
