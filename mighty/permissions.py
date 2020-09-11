from rest_framework.permissions import BasePermission

# Check if permission is satisfied
class HasMightyPermission(BasePermission):
    def has_permission(self, request, view):
        model = view.model()
        action = str(view.__class__.__name__)
        return request.user.has_perm(model.perm(action))

# Check if is about User
class IsMePermission(BasePermission):
    def has_permission(self, request, view):
        model = view.model()
        action = str(view.__class__.__name__)
        return request.user.has_perm(model.perm(action))
