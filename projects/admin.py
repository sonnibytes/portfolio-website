from django.contrib import admin
from .models import (
    Technology, SystemType, SystemModule,
    SystemImage, SystemFeature
)


# @admin.register(Technology)
# class TechnologyAdmin(admin.ModelAdmin):
#     list_display = ('name', 'slug', 'color')
#     prepopulated_fields = {'slug': ('name',)}
#     search_fields = ('name',)


# @admin.register(SystemType)
# class SystemTypeAdmin(admin.ModelAdmin):
#     list_display = ('name', 'code', 'slug', 'color')
#     prepopulated_fields = {'slug': ('name',)}
#     search_fields = ('name', 'description')


# class SystemImageInline(admin.TabularInline):
#     model = SystemImage
#     extra = 1


# class SystemFeatureInline(admin.TabularInline):
#     model = SystemFeature
#     extra = 1


# @admin.register(SystemModule)
# class SystemModuleAdmin(admin.ModelAdmin):
#     list_display = (
#         'title',
#         'system_id',
#         'system_type',
#         'status',
#         'created',
#         'completion_percent',
#         'featured'
#         )
#     list_filter = ('status', 'created', 'system_type', 'technologies', 'featured')
#     search_fields = ('title', 'subtitle', 'excerpt', 'content')
#     prepopulated_fields = {'slug': ('title',)}
#     filter_horizontal = ('technologies', 'related_projects')
#     inlines = [SystemFeatureInline, SystemImageInline]
#     date_hierarchy = 'created'

#     fieldsets = (
#         ("Basic Information", {
#             "fields": ("title", "slug", "system_id", "subtitle", "excerpt", "status"),
#         }),
#         ("Content", {
#             "fields": ("content", "challenges", "solutions", "outcome"),
#         }),
#         ("Classification", {
#             "fields": ("system_type", "technologies", "related_projects"),
#         }),
#         ("Technical Details", {
#             "fields": ("github_url", "live_url", "demo_url", "complexity", "completion_percent"),
#         }),
#         ("Dates", {
#             "fields": ("start_date", "end_date"),
#         }),
#         ("Media", {
#             "fields": ("thumbnail", "banner_image", "featured_image"),
#         }),
#         ("Featured", {
#             "fields": ("featured", "author"),
#             "classes": ("collapse",),
#         }),
#     )

#     def save_model(self, request, obj, form, change):
#         # Set author automatically if not provided
#         if not obj.author_id:
#             obj.author = request.user
#         super().save_model(request, obj, form, change)


# @admin.register(SystemImage)
# class SystemImageAdmin(admin.ModelAdmin):
#     list_display = ('system', 'caption', 'order')
#     list_filter = ('system',)
#     search_fields = ('caption', 'system__title')


# @admin.register(SystemFeature)
# class SystemFeatureAdmin(admin.ModelAdmin):
#     list_display = ('title', 'system', 'order')
#     list_filter = ('system',)
#     search_fields = ('title', 'desscription', 'system__title')
