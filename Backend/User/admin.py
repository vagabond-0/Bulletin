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

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    fields = ('alumni', 'comment_text', 'posted_date')  

@admin.register(Alumni)
class AlumniAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'company', 'designation')
    search_fields = ('user__username', 'email', 'company')
    inlines = [PostInline]

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('alumni', 'posted_date', 'description', 'likes')
    list_filter = ('posted_date', 'alumni')
    search_fields = ('alumni__user__username', 'description')
    date_hierarchy = 'posted_date'
    inlines = [CommentInline]  

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'alumni', 'comment_text', 'posted_date')
    list_filter = ('posted_date', 'alumni')
    search_fields = ('alumni__user__username', 'comment_text')
    date_hierarchy = 'posted_date'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
