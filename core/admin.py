from django.contrib import admin
from .models import Profile, Post, Comment


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'get_followers_count', 'created_at')
    search_fields = ('user__username', 'bio', 'location')
    readonly_fields = ('created_at',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'content_preview', 'get_likes_count', 'get_comments_count', 'created_at')
    search_fields = ('author__username', 'content')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')

    def content_preview(self, obj):
        return obj.content[:60]
    content_preview.short_description = 'Content'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'content_preview', 'parent', 'created_at')
    search_fields = ('author__username', 'content')
    list_filter = ('created_at',)

    def content_preview(self, obj):
        return obj.content[:60]
    content_preview.short_description = 'Content'
