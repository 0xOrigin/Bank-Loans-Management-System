from core.permissions import BaseBankPermissions


class BankPermissions(BaseBankPermissions):

    def has_permission(self, request, view):
        if view.action == 'list':
            return request.user.is_superuser
        return super().has_permission(request, view)
