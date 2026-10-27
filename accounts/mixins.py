from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

# Convenience role groups
MANAGEMENT_ROLES = ["SUPER_ADMIN", "PRINCIPAL", "ADMIN"]
FINANCE_ROLES = MANAGEMENT_ROLES + ["ACCOUNTANT"]
STAFF_ROLES = MANAGEMENT_ROLES + ["TEACHER", "ACCOUNTANT", "LIBRARIAN", "STAFF"]
FAMILY_ROLES = ["STUDENT", "PARENT"]
ALL_ROLES = STAFF_ROLES + FAMILY_ROLES


class RoleRequiredMixin(LoginRequiredMixin):
    """Class-based view mixin: only lets the given roles (or superusers) through."""
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.is_superuser or request.user.role in self.allowed_roles:
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied("You do not have permission to access this page.")


TEACHING_ROLES = MANAGEMENT_ROLES + ["TEACHER"]
