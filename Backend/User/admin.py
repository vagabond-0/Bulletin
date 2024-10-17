from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Alumni, Post, Comment

class AlumniInline(admin.StackedInline):
    model = Alumni
    can_delete = False
    verbose_name_plural = 'alumni'

class UserAdmin(BaseUserAdmin):
    inlines = (AlumniInline,)

class PostInline(admin.TabularInline):
    model = Post
    extra = 1
    fields = ('description', 'posted_date', 'get_likes_count')
    readonly_fields = ('get_likes_count', 'posted_date')

    def get_likes_count(self, instance):
        return instance.likes.count()
    get_likes_count.short_description = 'Likes'

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    fields = ('alumni', 'comment_text', 'posted_date')
    readonly_fields = ('posted_date',)

@admin.register(Alumni)
class AlumniAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'company', 'designation', 'get_likes_received')
    search_fields = ('user__username', 'email', 'company')
    inlines = [PostInline]

    def get_likes_received(self, obj):
        return obj.likes.count()
    get_likes_received.short_description = 'Likes Received'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('alumni', 'posted_date', 'description', 'get_likes_count')
    list_filter = ('posted_date', 'alumni')
    search_fields = ('alumni__user__username', 'description')
    date_hierarchy = 'posted_date'
    inlines = [CommentInline]

    def get_likes_count(self, obj):
        return obj.likes.count()
    get_likes_count.short_description = 'Likes'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'alumni', 'comment_text', 'posted_date')
    list_filter = ('posted_date', 'alumni')
    search_fields = ('alumni__user__username', 'comment_text')
    date_hierarchy = 'posted_date'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)