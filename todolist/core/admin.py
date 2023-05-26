from django.contrib import admin

from core.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group


# Register your models here.


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    fieldsets = (
        (None, {'fields': ('username',)}),
        ('Personal Information', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Special dates', {'fields': ('last_login', 'date_joined')}),
    )


admin.site.unregister(Group)