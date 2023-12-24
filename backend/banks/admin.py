from django.contrib import admin
from core.admin import BankAdmin
from banks.models import Bank, Branch


@admin.register(Bank)
class BankAdmin(BankAdmin):
    list_display = BankAdmin.list_display + ['name_en', 'name_ar']
    search_fields = ['name_en', 'name_ar',]


@admin.register(Branch)
class BranchAdmin(BankAdmin):
    list_display = BankAdmin.list_display + ['name_en', 'name_ar', 'code', 'bank']
    search_fields = ['name_en', 'name_ar', 'code',]
    list_filter = ['bank']
