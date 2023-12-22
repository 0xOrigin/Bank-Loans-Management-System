from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.conf import settings


User = get_user_model()

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'last_login', 'is_superuser', 'is_staff')
    search_fields = ('username', 'email')
    readonly_fields = ('last_login', 'created_at', 'updated_at', 'deleted_at')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'picture',)}),
        ('Permissions', {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
        ('Important dates', {
                'fields': ('last_login', 'created_at', 'updated_at', 'deleted_at'),
            }
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('username', 'email', 'password1', 'password2'),
            },
        ),
    ) 
    exclude = ()

    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    ordering = ('username',)
    filter_horizontal = (
        'groups',
        'user_permissions',
    )
    list_per_page = settings.PAGINATION_ADMIN_PAGE_SIZE