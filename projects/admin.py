from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    SystemModule,
    SystemType,
    Technology,
    SystemFeature,
    SystemImage,
    SystemMetric,
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
    readonly_fields = ("timestamp",)


@admin.register(SystemModule)
class SystemModuleAdmin(admin.ModelAdmin):
    list_display = (
        "system_id",
        "title",
        "system_type",
        "status_display",
        "completion_progress",
        "complexity_display",
        "featured",
        "created",
        "author",
    )
    list_filter = (
        "status",
        "system_type",
        "complexity",
        "featured",
        "created",
        "technologies",
        "priority",
    )
    search_fields = ("title", "system_id", "description", "technical_details")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("technologies", "related_systems")
    readonly_fields = ("system_id", "created", "updated")
    date_hierarchy = "created"
    ordering = ("-created",)

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
            "Technical Specifications",
            {
                "fields": (
                    "technologies",
                    "complexity",
                    "priority",
                    "completion_percent",
                    "performance_score",
                    "uptime_percentage",
                )
            },
        ),
        (
            "URLs and Links",
            {
                "fields": ("github_url", "live_url", "demo_url", "documentation_url"),
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
            "Status and Dates",
            {
                "fields": (
                    "status",
                    "start_date",
                    "end_date",
                    "deployment_date",
                    "created",
                    "updated",
                )
            },
        ),
        ("Related Systems", {"fields": ("related_systems",), "classes": ("collapse",)}),
    )

    inlines = [SystemFeatureInline, SystemImageInline, SystemMetricInline]

    def status_display(self, obj):
        color = obj.get_status_color()
        return format_html(
            '<span style="color: {}; font-weight: bold;">● {}</span>',
            color,
            obj.get_status_display(),
        )

    status_display.short_description = "Status"
    status_display.admin_order_field = "status"

    def completion_progress(self, obj):
        progress = obj.get_development_progress()
        color = (
            "#27c93f" if progress >= 100 else "#ffbd2e" if progress >= 50 else "#ff6b8b"
        )
        return format_html(
            '<div style="width: 100px; background: #333; border-radius: 10px; overflow: hidden;">'
            '<div style="width: {}%; height: 20px; background: {}; border-radius: 10px;"></div>'
            "</div> {}%",
            progress,
            color,
            progress,
        )

    completion_progress.short_description = "Progress"

    def complexity_display(self, obj):
        return obj.get_complexity_display()

    complexity_display.short_description = "Complexity"
    complexity_display.admin_order_field = "complexity"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("system_type", "author")

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(SystemFeature)
class SystemFeatureAdmin(admin.ModelAdmin):
    list_display = ("title", "system", "feature_type", "implementation_status", "order")
    list_filter = ("feature_type", "implementation_status", "system__system_type")
    search_fields = ("title", "description", "system__title")
    ordering = ("system", "order")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("system")


@admin.register(SystemImage)
class SystemImageAdmin(admin.ModelAdmin):
    list_display = ("system", "image_type", "caption", "order")
    list_filter = ("image_type", "system__system_type")
    search_fields = ("caption", "alt_text", "system__title")
    ordering = ("system", "order")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("system")


@admin.register(SystemMetric)
class SystemMetricAdmin(admin.ModelAdmin):
    list_display = (
        "system",
        "metric_name",
        "metric_value",
        "metric_unit",
        "metric_type",
        "is_current",
        "timestamp",
    )
    list_filter = ("metric_type", "is_current", "timestamp", "system__system_type")
    search_fields = ("metric_name", "system__title", "system__system_id")
    readonly_fields = ("timestamp",)
    ordering = ("-timestamp",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("system")


# Customize admin site header
admin.site.site_header = "ML DEVLOG System Administration"
admin.site.site_title = "ML DEVLOG Admin"
admin.site.index_title = "System Control Panel"
