from rest_framework.permissions import BasePermission, SAFE_METHODS


class HasConferenceRoomBookPermission(BasePermission):
    """
    Custom permission: only employees with role 'lead' or 'manager' can create or edit.
    Read-only access is allowed to others.
    """
    message = "Only employee with role 'lead' or 'manager' are allowed to perform this create action."

    def has_permission(self, request, view):
        user = request.user
        if not user or user.is_authenticated is False:
            return False
        # Allow read-only methods for everyone
        if request.method in SAFE_METHODS:
            return True
        
        # Only allow POST (create) and PUT/PATCH (edit) for lead or manager
        return user.has_perm("employee.add_bookconferenceroom") or user.has_perm("employee.change_bookconferenceroom")


class IsSuperUserOrReadOnly(BasePermission):
    
    """
    Custom permission:
    - Superusers have full access (read/write).
    - Authenticated users (non-superusers) have read-only access.
    - Unauthenticated users have no access.
    """

    def has_permission(self, request, view):
        
        user = request.user

        if not user or user.is_authenticated is False:
            return False
        elif user.is_superuser:
            return True
        return request.method in SAFE_METHODS
