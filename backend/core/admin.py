from django.contrib import admin
from django.conf import settings
from django.utils import timezone


class BankAdmin(admin.ModelAdmin):
    list_display = ['id',]
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by', 'deleted_by']
    list_per_page = settings.PAGINATION_ADMIN_PAGE_SIZE
    actions = ['soft_delete_selected',]

    def soft_delete_selected(self, request, queryset):
        deleted_by = request.user.pk
        deleted_at = timezone.now()
        queryset.update(deleted_by=deleted_by, deleted_at=deleted_at)
    
    soft_delete_selected.allowed_permissions = ('delete',)
    soft_delete_selected.short_description = 'Soft delete selected %(verbose_name_plural)s'
