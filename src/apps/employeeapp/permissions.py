from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsManagerOrLead(BasePermission):
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
        return user.employee.manager or user.employee.lead
