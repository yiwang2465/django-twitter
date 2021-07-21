from rest_framework.permissions import BasePermission


class IsObjectOwner(BasePermission):
    """
    detail=False will check has_permission
    detail=True will check has_permission and has_object_permission
    define error message
    """
    message = 'You do not have permission to access this object'

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user
