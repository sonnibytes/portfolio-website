from django.contrib import admin
from .models import Post, Category, Tag, Comment, Series, SeriesPost, PostView
from django.utils import timezone


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'status', 'created',
                    'published_date', 'featured')
    list_filter = ('status', 'created', 'published_date', 'author',
                   'category', 'featured')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'published_date'
    filter_horizontal = ('tags',)
    readonly_fields = ('reading_time',)
    ordering = ('status', '-published')

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'content')
        }),
        ('Meta Information', {
            'fields': ('excerpt', 'category', 'tags', 'featured')
        }),
        ('Images', {
            'fields': ('thumbnail', 'banner_image')
        }),
        ('Featured Content', {
            'fields': ('featured_code', 'show_toc')
        }),
        ('Publication', {
            'fields': ('status', 'published_date', 'reading_time')
        }),
    )

    def save_model(self, request, obj, form, change):
        if obj.status == 'published' and not obj.published_date:
            obj.published_date = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'post', 'created', 'approved')
    list_filter = ('approved', 'created')
    search_fields = ('name', 'email', 'content')
    actions = ['approve_comment']

    def approve_comment(self, request, queryset):
        queryset.update(approved=True)
    approve_comment.short_desciption = "Approve selected comments"


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'get_posts_count')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'description')

    def get_posts_count(self, obj):
        return obj.post.count()
    get_posts_count.short_description = 'Posts'


@admin.register(SeriesPost)
class SeriesPostAdmin(admin.ModelAdmin):
    list_display = ('series', 'post', 'order')
    list_filter = ('series',)
    raw_id_fields = ('post',)
    ordering = ('series', 'order')
