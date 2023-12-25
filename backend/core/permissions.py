from rest_framework import permissions
from rest_framework.permissions import DjangoModelPermissions


class BaseBankPermissions(DjangoModelPermissions):

    def has_permission(self, request, view):
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj)
