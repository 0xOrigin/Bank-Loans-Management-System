from rest_framework import permissions
from rest_framework.permissions import DjangoModelPermissions


class AuthenticationPermissions(DjangoModelPermissions):

    def has_permission(self, request, view):
        if view.action == 'list':
            return request.user.is_superuser
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id or request.user.is_superuser
