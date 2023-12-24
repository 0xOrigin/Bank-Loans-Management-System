from django.contrib import admin
from core.admin import BaseBankAdmin
from banks.models import Bank, Branch


@admin.register(Bank)
class BankAdmin(BaseBankAdmin):
    list_display = BaseBankAdmin.list_display + ['name_en', 'name_ar']
    search_fields = ['name_en', 'name_ar',]


@admin.register(Branch)
class BranchAdmin(BaseBankAdmin):
    list_display = BaseBankAdmin.list_display + ['name_en', 'name_ar', 'code', 'bank']
    search_fields = ['name_en', 'name_ar', 'code',]
    list_filter = ['bank']
