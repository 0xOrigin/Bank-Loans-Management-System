from django.contrib import admin
from core.admin import BaseBankAdmin
from loans.models import LoanPlan, Loan, LoanPayment


@admin.register(LoanPlan)
class LoanPlanAdmin(BaseBankAdmin):
    list_display = BaseBankAdmin.list_display
    search_fields = ['annual_interest_rate', 'duration_in_months']


@admin.register(Loan)
class LoanAdmin(BaseBankAdmin):
    list_display = BaseBankAdmin.list_display + ['purpose', 'amount', 'plan', 'status', 'is_active', 'is_amortized']
    search_fields = ['purpose', 'amount', 'plan', 'customer', 'status', 'is_active', 'is_amortized', 'total_payable_amount', 'monthly_payable_amount', 'approved_at', 'released_at']
    list_filter = ['plan', 'status', 'is_active', 'is_amortized', 'approved_at', 'released_at']


@admin.register(LoanPayment)
class LoanPaymentAdmin(BaseBankAdmin):
    list_display = BaseBankAdmin.list_display
    search_fields = ['installment_number', 'loan', 'amount',]
    list_filter = ['is_paid',]
