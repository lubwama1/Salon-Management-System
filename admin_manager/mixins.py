from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from users.models import CustomUser

class AdminRequiredMixin(UserPassesTestMixin):
    """Verify that the current user is an admin."""
    raise_exception = True

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == CustomUser.UserRoleChoices.ADMIN

    def handle_no_permission(self):
        """Override to return a custom response when permission is denied."""
        if self.request.user.is_authenticated:
            raise PermissionDenied("You do not have admin privileges to access this page.")
        return super().handle_no_permission()