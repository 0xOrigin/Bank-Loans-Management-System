from core.permissions import BaseBankPermissions
from authentication.apps import AuthenticationConfig


class BankPermissions(BaseBankPermissions):

    def has_permission(self, request, view):
        if view.action == 'list':
            return request.user.is_superuser
        return super().has_permission(request, view)


class ApproveApplicantPermissions(BaseBankPermissions):

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.has_perm(f'{AuthenticationConfig.name}.can_approve_applicant')


class RejectApplicantPermissions(BaseBankPermissions):
    
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.has_perm(f'{AuthenticationConfig.name}.can_reject_applicant')
