from django.contrib import admin
from django.utils.html import format_html
from .models import (
    SystemModule,
    SystemType,
    Technology,
    SystemFeature,
    SystemImage,
    SystemMetric,
    SystemDependency,
    GitHubRepository,
    GitHubLanguage,
    ArchitectureComponent,
    ArchitectureConnection,
    SystemSkillGain
)
from core.admin_mixins import TechnologyCSVImportMixin, SystemTypeCSVImportMixin

# ========== NEW: SYSTEM SKILL GAIN ADMIN ==========

@admin.register(SystemSkillGain)
class SystemSkillGainAdmin(admin.ModelAdmin):
    """Management of skill gains from projects"""
    list_display = [
        'system',
        'skill',
        'proficiency_gained_display',
        'tech_count',
        'how_learned_short'
    ]

    list_filter = [
        'proficiency_gained',
        'skill__category',
        'system__status',
        'system__learning_stage'
    ]

    search_fields = [
        'skill__name',
        'system__title',
        'how_learned',
    ]

    autocomplete_fields = ['skill', 'system']
    filter_horizontal = ['technologies_used']  # New field
    list_select_related = ['skill', 'system']

    fieldsets = (
        ('Learning Context', {
            'fields': ('system', 'skill', 'proficiency_gained')
        }),
        ('Technologies Applied', {
            'fields': ('technologies_used',),
            'description': 'Which technologies were used to apply this skill in this project'
        }),
        ('Learning Details', {
            'fields': ('how_learned',),
            'classes': ('collapse',)
        }),
    )

    def proficiency_gained_display(self, obj):
        colors = {
            1: '#ff8a80',  # Light red
            2: '#ffbd2e',  # Yellow
            3: '#00f0ff',  # Cyan
            4: '#27c93f',  # Green
            5: '#9c27b0',  # Purple
        }
        color = colors.get(obj.proficiency_gained, '#999')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_proficiency_gained_display()
        )
    proficiency_gained_display.short_description = "Proficiency Level"

    def tech_count(self, obj):
        count = obj.technologies_used.count()
        if count > 0:
            return format_html('<span style="color: #00f0ff;">{}</span>', count)
        return format_html('<span style="color: #999;">0</span>')
    tech_count.short_description = "Tech Used"

    def how_learned_short(self, obj):
        if obj.how_learned:
            return obj.how_learned[:50] + "..." if len(obj.how_learned) > 50 else obj.how_learned
        return "-"
    how_learned_short.short_description = "How Learned"


# ============================================================================
# ARCHITECTURE COMPONENTS ADMIN
# ============================================================================

class ArchitectureComponentInline(admin.TabularInline):
    """Inline editing of architecture components within SystemModule admin"""
    model = ArchitectureComponent
    extra = 0
    fields = (
        'name', 'component_type', 'technology',
        'position_x', 'position_y', 'position_z', 
        'color', 'size', 'is_core', 'display_order'
    )
    classes = ('collapse',)

class ArchitectureConnectionInline(admin.TabularInline):
    """Inline editing of connections within ArchitectureComponent admin"""
    model = ArchitectureConnection
    fk_name = 'from_component'
    extra = 0
    fields = ('to_component', 'connection_type', 'label', 'line_color', 'is_bidirectional')
    classes = ('collapse',)

@admin.register(ArchitectureComponent)
class ArchitectureComponentAdmin(admin.ModelAdmin):
    """Architecture Component management"""
    list_display = ('name', 'system', 'component_type', 'technology', 'is_core')
    list_filter = ('component_type', 'is_core', 'system__system_type')
    search_fields = ('name', 'system__title', 'description')
    list_select_related = ('system', 'technology')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('system', 'name', 'component_type', 'description', 'technology')
        }),
        ('3D Positioning', {
            'fields': ('position_x', 'position_y', 'position_z'),
            'description': 'Position in 3D space. Origin (0,0,0) is center. Range: -5 to +5'
        }),
        ('Visual Styling', {
            'fields': ('color', 'size', 'is_core', 'display_order'),
            'description': 'Visual appearance in architecture diagram'
        }),
    )
    
    inlines = [ArchitectureConnectionInline]

@admin.register(ArchitectureConnection)
class ArchitectureConnectionAdmin(admin.ModelAdmin):
    """Architecture Connection management"""
    list_display = ('from_component', 'to_component', 'connection_type', 'is_bidirectional')
    list_filter = ('connection_type', 'is_bidirectional')
    search_fields = ('from_component__name', 'to_component__name', 'label')
    list_select_related = ('from_component', 'to_component')

# =======================================

@admin.register(Technology)
class TechnologyAdmin(TechnologyCSVImportMixin, admin.ModelAdmin):
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
class SystemTypeAdmin(SystemTypeCSVImportMixin, admin.ModelAdmin):
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

# New with Skill-Tech Rework
class SystemSkillGainInline(admin.TabularInline):
    """Inline editing of skill gains within SystemModule admin"""
    model = SystemSkillGain
    extra = 0
    fields = ['skill', 'proficiency_gained', 'how_learned']
    autocomplete_fields = ['skill']
    verbose_name = "Skill Gained"
    verbose_name_plural = "Skills Gained"


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
    filter_horizontal = ("technologies",)
    readonly_fields = (
        "system_id",
        "created_at",
        "updated_at",
        "get_health_status",
        "completion_trend",
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    inlines = [SystemFeatureInline, SystemImageInline, SystemMetricInline, ArchitectureComponentInline, SystemSkillGainInline]

    # Add admin action for creating default architectures
    actions = ['create_default_architecture']

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
                    "usage_examples",
                    "setup_instructions",
                    "challenges",
                    # "future_enhancements",
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
                    # "architecture_diagram",
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
        percent = obj.completion_percent
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

    # ============= ARCHITECTURE UPDATES =========================

    def create_default_architecture(self, request, queryset):
        """Admin action to create default architecture for selected systems"""
        from .services.architecture_service import ArchitectureDiagramService
        
        count = 0
        for system in queryset:
            if not system.has_architecture_diagram():
                # Auto-detect architecture type
                arch_type = self._determine_architecture_type(system)
                ArchitectureDiagramService.create_default_architecture(system, arch_type)
                count += 1
        
        self.message_user(request, f'Created default architecture for {count} systems.')
    
    create_default_architecture.short_description = "Create default architecture diagrams"
    
    def _determine_architecture_type(self, system):
        """Auto-detect appropriate architecture type"""
        techs = [tech.name.lower() for tech in system.technologies.all()]
        title = system.title.lower()
        
        if 'streamlit' in techs or ('map' in title and 'buddy' in title):
            return 'data_pipeline'
        elif 'django' in techs or 'flask' in techs:
            return 'web_app'
        elif 'fastapi' in techs or 'api' in title:
            return 'api_service'
        elif any(ml_tech in techs for ml_tech in ['scikit-learn', 'tensorflow', 'pytorch']):
            return 'ml_project'
        else:
            return 'web_app'


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


@admin.register(GitHubRepository)
class GitHubRepositoryAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "language",
        "stars_count",
        "forks_count",
        "is_private",
        "is_active",
        "last_synced",
    ]
    list_filter = ["language", "is_private", "is_fork", "is_archived", "last_synced"]
    search_fields = ["name", "full_name", "description"]
    readonly_fields = [
        "github_id",
        "github_created_at",
        "github_updated_at",
        "last_synced",
    ]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("name", "full_name", "description", "related_system")},
        ),
        ("GitHub Data", {"fields": ("github_id", "html_url", "clone_url", "homepage")}),
        (
            "Statistics",
            {
                "fields": (
                    "stars_count",
                    "forks_count",
                    "watchers_count",
                    "size",
                    "language",
                )
            },
        ),
        ("Flags", {"fields": ("is_private", "is_fork", "is_archived")}),
        (
            "Timestamps",
            {
                "fields": ("github_created_at", "github_updated_at", "last_synced"),
                "classes": ("collapse",),
            },
        ),
    )

    def is_active(self, obj):
        return obj.is_recently_active

    is_active.boolean = True
    is_active.short_description = "Recently Active"


class GitHubLanguageInline(admin.TabularInline):
    model = GitHubLanguage
    extra = 0
    readonly_fields = ["language", "bytes_count", "percentage"]


# Update GitHubRepositoryAdmin to include inline
GitHubRepositoryAdmin.inlines = [GitHubLanguageInline]


# Customize admin site
admin.site.site_header = "AURA Portfolio Administration"
admin.site.site_title = "AURA Admin"
admin.site.index_title = "Systems Control Panel"
