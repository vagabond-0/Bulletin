from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Alumni

class AlumniInline(admin.StackedInline):
    model = Alumni
    can_delete = False
    verbose_name_plural = 'alumni'

class UserAdmin(BaseUserAdmin):
    inlines = (AlumniInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Alumni)