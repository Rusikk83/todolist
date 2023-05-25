from django.contrib import admin

from core.models import User
from django.contrib.auth.admin import UserAdmin


# Register your models here.
@admin.register(User)
class MyUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'first_name', 'last_name')
    exclude = ("password",)
    readonly_fields = ('last_login', 'date_joined')

    search_fields = ('username', 'email', 'first_name', 'last_name', )
    filter_horizontal = ()
    list_filter = ('is_staff', 'is_active', 'is_superuser', )
    list_per_page = 10
    list_max_show_all = 100

    # def get_form(self, request, obj=None, **kwargs):
    #     form = super(MyUserAdmin, self).get_form(request, obj, **kwargs)
    #     del form.base_fields['groups']
    #     return form
