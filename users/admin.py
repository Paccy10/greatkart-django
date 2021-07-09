from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import User, UserProfile


class UserAdmin(BaseUserAdmin):

    list_display = ('firstname', 'lastname', 'email', 'username',
                    'last_login', 'date_joined', 'is_active')
    list_display_links = ('firstname', 'lastname', 'email')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class UserProfileAdmin(admin.ModelAdmin):

    def thumbnail(self, profile):
        return format_html(f'<img src="{profile.profile_picture.url}" \
            width="30" style="border-radius:50%;"/>')

    thumbnail.short_description = 'Profile Picture'

    list_display = ('thumbnail', 'user', 'city', 'state', 'country')


admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
