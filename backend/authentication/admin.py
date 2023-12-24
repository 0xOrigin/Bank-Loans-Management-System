from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.conf import settings
from core.admin import BaseBankAdmin
from authentication.models import BankPersonnel, LoanProvider, LoanCustomer

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin, BaseBankAdmin):
    list_display = ('username', 'email', 'last_login', 'is_superuser', 'is_staff')
    search_fields = ('username', 'email')
    readonly_fields = ('role', 'last_login', 'created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by', 'deleted_by')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'picture',)}),
        ('Permissions', {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'role',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
        ('Important dates & logs', {
                'fields': ('last_login', 'created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by', 'deleted_by'),
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


@admin.register(BankPersonnel)
class BankPersonnelAdmin(BaseBankAdmin):
    list_display = BaseBankAdmin.list_display + ['user',]
    search_fields = ['user__username', 'user__email', 'branch__bank__name_en', 'branch__bank__name_ar']
    list_filter = ['branch__bank',]


@admin.register(LoanProvider)
class LoanProviderAdmin(BaseBankAdmin):
    list_display = BaseBankAdmin.list_display + ['user',]
    search_fields = ['user__username', 'user__email',]


@admin.register(LoanCustomer)
class LoanCustomerAdmin(BaseBankAdmin):
    list_display = BaseBankAdmin.list_display + ['user',]
    search_fields = ['user__username', 'user__email',]
