from core.permissions import BaseBankPermissions
from loans.apps import LoansConfig


class ApproveLoanPermissions(BaseBankPermissions):

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.has_perm(f'{LoansConfig.name}.can_approve_loan')


class ReleaseLoanPermissions(BaseBankPermissions):

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.has_perm(f'{LoansConfig.name}.can_release_loan')


class DisburseLoanPermissions(BaseBankPermissions):
    
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.has_perm(f'{LoansConfig.name}.can_disburse_loan')


class RejectLoanPermissions(BaseBankPermissions):
    
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.has_perm(f'{LoansConfig.name}.can_reject_loan')


class PayLoanPermissions(BaseBankPermissions):
    
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.has_perm(f'{LoansConfig.name}.can_pay_loan')


class AmortizationSchedulePermissions(BaseBankPermissions):
    
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.has_perm(f'{LoansConfig.name}.can_view_amortization_schedule')
