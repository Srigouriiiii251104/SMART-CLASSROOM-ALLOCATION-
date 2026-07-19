from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


class RoleRequiredMixin:
    allowed_roles: tuple[str, ...] = ()

    def dispatch(self, request, *args, **kwargs):
        if self.allowed_roles and request.user.role not in self.allowed_roles:
            raise PermissionDenied("You do not have permission to access this page.")
        return super().dispatch(request, *args, **kwargs)


def role_required(*allowed_roles: str):
    return user_passes_test(
        lambda user: user.is_authenticated and user.role in allowed_roles,
        login_url="login",
    )
