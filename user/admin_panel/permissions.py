from rest_framework.permissions import BasePermission


class IsSuperAdminOrManager(BasePermission):
    """
    Custom permission to allow access only to users with role 'super_admin' or 'manager'.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['super_admin', 'manager']



