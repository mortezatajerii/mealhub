# accounts/permissions.py
from rest_framework.permissions import BasePermission


def role_required(*roles):
    class RolePermission(BasePermission):
        def has_permission(self, request, view):
            return request.user.is_authenticated and request.user.role in roles

    RolePermission.__name__ = f"RolePermission[{','.join(roles)}]"
    return RolePermission
