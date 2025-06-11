from django.contrib import admin
from django.utils.html import format_html
from .models import (
    SystemModule,
    SystemType,
    Technology,
    SystemFeature,
    SystemImage,
    SystemMetric,
    SystemDependency
)


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "color_preview",
        "icon_preview",
        "systems_count",
    )
    list_filter = ("category",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("category", "name")

    def color_preview(self, obj):
        if obj.color:
            return format_html(
                '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 3px; display: inline-block;"></div>',
                obj.color,
            )
        return "-"

    color_preview.short_description = "Color"

    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<i class="fas {}"></i> {}', obj.icon, obj.icon)
        return "-"

    icon_preview.short_description = "Icon"

    def systems_count(self, obj):
        count = obj.systems.filter(status__in=["deployed", "published"]).count()
        return f"{count} systems"

    systems_count.short_description = "Usage"


@admin.register(SystemType)
class SystemTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "color_preview",
        "icon_preview",
        "systems_count",
        "display_order",
    )
    list_editable = ("display_order",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("display_order", "name")

    def color_preview(self, obj):
        if obj.color:
            return format_html(
                '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 3px; display: inline-block;"></div>',
                obj.color,
            )
        return "-"

    color_preview.short_description = "Color"

    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<i class="fas {}"></i> {}', obj.icon, obj.icon)
        return "-"

    icon_preview.short_description = "Icon"

    def systems_count(self, obj):
        return obj.get_systems_count()

    systems_count.short_description = "Systems"


class SystemFeatureInline(admin.TabularInline):
    model = SystemFeature
    extra = 0
    fields = ("title", "feature_type", "implementation_status", "icon", "order")
    ordering = ("order",)


class SystemImageInline(admin.TabularInline):
    model = SystemImage
    extra = 0
    fields = ("image", "image_type", "caption", "alt_text", "order")
    ordering = ("order",)


class SystemMetricInline(admin.TabularInline):
    model = SystemMetric
    extra = 0
    fields = ("metric_name", "metric_value", "metric_unit", "metric_type", "is_current")
    readonly_fields = ("created_at",)


@admin.register(SystemModule)
class SystemModuleAdmin(admin.ModelAdmin):
    list_display = (
        "system_id",
        "title",
        "system_type",
        "status_display",
        "completion_progress",
        "health_display",
        "performance_display",
        "featured",
        "created_at",
    )
    list_filter = (
        "status",
        "system_type",
        "complexity",
        "featured",
        "team_size",
        "created_at",
    )
    search_fields = ("title", "system_id", "description")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("technologies", "related_systems")
    readonly_fields = (
        "system_id",
        "created_at",
        "updated_at",
        "get_health_status",
        "completion_trend",
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    inlines = [SystemFeatureInline, SystemImageInline, SystemMetricInline]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "title",
                    "slug",
                    "system_id",
                    "subtitle",
                    "excerpt",
                    "author",
                    "system_type",
                    "featured",
                )
            },
        ),
        (
            "Content",
            {
                "fields": (
                    "description",
                    "features_overview",
                    "technical_details",
                    "challenges",
                    "future_enhancements",
                )
            },
        ),
        (
            "Technical Details",
            {
                "fields": (
                    "github_url",
                    "live_url",
                    "demo_url",
                    "documentation_url",
                    "technologies",
                    "related_systems",
                )
            },
        ),
        (
            "Project Management",
            {
                "fields": (
                    "status",
                    "complexity",
                    "priority",
                    "completion_percent",
                    "start_date",
                    "end_date",
                    "deployment_date",
                    "estimated_completion_date",
                    "team_size",
                )
            },
        ),
        (
            "Development Metrics",
            {
                "fields": (
                    "estimated_dev_hours",
                    "actual_dev_hours",
                    "code_lines",
                    "commit_count",
                    "last_commit_date",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Performance Metrics",
            {
                "fields": (
                    "performance_score",
                    "uptime_percentage",
                    "response_time_ms",
                    "daily_users",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Media",
            {
                "fields": (
                    "thumbnail",
                    "banner_image",
                    "featured_image",
                    "architecture_diagram",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "System Health",
            {
                "fields": ("get_health_status", "completion_trend"),
                "classes": ("collapse",),
            },
        ),
    )

    def status_display(self, obj):
        colors = {
            "draft": "#808080",
            "in_development": "#ffbd2e",
            "testing": "#00f0ff",
            "deployed": "#27c93f",
            "published": "#27c93f",
            "archived": "#b39ddb",
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, "#808080"),
            obj.get_status_display(),
        )

    status_display.short_description = "Status"

    def completion_progress(self, obj):
        percent = obj.get_completion_percentage()
        if percent >= 90:
            color = "#27c93f"
        elif percent >= 50:
            color = "#ffbd2e"
        else:
            color = "#ff8a80"

        return format_html(
            '<div style="width: 100px; background: #f0f0f0; border-radius: 5px;">'
            '<div style="width: {}%; background: {}; height: 20px; border-radius: 5px; '
            'text-align: center; line-height: 20px; color: white; font-size: 12px;">{}</div></div>',
            percent,
            color,
            f"{percent}%",
        )

    completion_progress.short_description = "Progress"

    def health_display(self, obj):
        status = obj.get_health_status()
        colors = {
            "excellent": "#27c93f",
            "good": "#00f0ff",
            "fair": "#ffbd2e",
            "poor": "#ff8a80",
            "unknown": "#808080",
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(status, "#808080"),
            status.title(),
        )

    health_display.short_description = "Health"

    def performance_display(self, obj):
        if obj.performance_score:
            score = float(obj.performance_score)
            if score >= 90:
                color = "#27c93f"
            elif score >= 70:
                color = "#ffbd2e"
            else:
                color = "#ff8a80"
            return format_html('<span style="color: {};">{}/100</span>', color, score)
        return "-"

    performance_display.short_description = "Performance"


@admin.register(SystemDependency)
class SystemDependencyAdmin(admin.ModelAdmin):
    list_display = (
        "system",
        "depends_on",
        "dependency_type",
        "critical_status",
        "created_at",
    )
    list_filter = ("dependency_type", "is_critical", "created_at")
    search_fields = ("system__title", "depends_on__title", "description")
    readonly_fields = ("created_at",)

    def critical_status(self, obj):
        if obj.is_critical:
            return format_html('<span style="color: #f44336;">🔴 Critical</span>')
        else:
            return format_html('<span style="color: #27c93f;">🟢 Normal</span>')

    critical_status.short_description = "Criticality"


@admin.register(SystemFeature)
class SystemFeatureAdmin(admin.ModelAdmin):
    list_display = ("title", "system", "feature_type", "implementation_status", "order")
    list_filter = ("feature_type", "implementation_status")
    search_fields = ("title", "description", "system__title")
    ordering = ("system", "order")


@admin.register(SystemImage)
class SystemImageAdmin(admin.ModelAdmin):
    list_display = ("system", "image_type", "caption", "order")
    list_filter = ("image_type",)
    search_fields = ("caption", "alt_text", "system__title")
    ordering = ("system", "order")


@admin.register(SystemMetric)
class SystemMetricAdmin(admin.ModelAdmin):
    list_display = (
        "system",
        "metric_name",
        "metric_value",
        "metric_unit",
        "metric_type",
        "is_current",
        "created_at",
    )
    list_filter = ("metric_type", "is_current", "created_at")
    search_fields = ("metric_name", "system__title")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)


# Customize admin site
admin.site.site_header = "AURA Portfolio Administration"
admin.site.site_title = "AURA Admin"
admin.site.index_title = "Systems Control Panel"
