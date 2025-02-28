from django.db.models import Q

from mighty.functions import setting

base_action = ['list', 'detail', 'delete', 'retrieve', 'create', 'update', 'partial_update', 'destroy']
base_permission = ['is_superuser', 'is_staff', 'is_me']


class MightyPermission:
    obj = None
    request = None
    view = None
    user = None
    model = None
    user_way = 'user'
    user_perms_list = []
    user_perms_retrieve = []
    user_perms_create = []
    user_perms_update = []
    user_perms_partial_update = []
    user_perms_destroy = []
    user_perms_default = []

    def has_perm(self, perm):
        return self.user.has_perm(perm)

    def Q_is_me(self, prefix=''):
        return Q(**{prefix + self.user_way: self.request.user})

    """ Properties """
    @property
    def user(self):
        return self.request.user

    @property
    def is_authenticated(self):
        return self.user.is_authenticated

    @property
    def user_groups(self):
        return self.user.groups.all()

    @property
    def user_groups_pk(self):
        return [group.pk for group in self.user_groups]

    @property
    def is_staff(self):
        return self.user.is_staff

    @property
    def is_superuser(self):
        return self.user.is_superuser

    def is_me(self):
        raise NotImplementedError('Subclasses should implement is_me')

    """ Permissions by action """
    def can_list(self):
        return self.check_user_permissions('list')

    def can_retrieve(self):
        return self.check_user_permissions('retrieve')

    def can_create(self):
        return self.check_user_permissions('create')

    def can_update(self):
        return self.check_user_permissions('update')

    def can_partial_update(self):
        return self.check_user_permissions('partial_update')

    def can_destroy(self):
        return self.check_user_permissions('destroy')

    def can_default(self):
        return self.check_user_permissions('default')

    def can_default_unauth(self):
        return False

    """ Check if action has permission """
    def can_check_action(self, action):
        check_action = getattr(self, 'check_' + action)
        if len(check_action):
            return any(getattr(self, check) for check in check_action)
        return any(getattr(self, check) for check in self.check_others)

    """ Loop on permission action """
    def check_user_permissions(self, action):
        user_perms = 'user_perms_' + action
        if action != 'default' and hasattr(self, user_perms) and len(getattr(self, user_perms)):
            return any(getattr(self, perm)() for perm in getattr(self, user_perms))
        if len(self.user_perms_default):
            return any(getattr(self, perm)() for perm in self.user_perms_default)
        return True

    def check_by_action(self, action):
        if action:
            can_action = 'can_' + action
            if hasattr(self, can_action):
                return getattr(self, can_action)()
        return self.can_default()

    def check_permission(self):
        if self.request.user.is_authenticated:
            if hasattr(self.view, 'action'):
                return self.check_by_action(self.view.action)
            return self.can_default()
        return self.can_default_unauth()

    def has_permission(self, request, view):
        self.request = request
        self.view = view
        return self.check_permission()

    def has_object_permission(self, request, view, obj):
        self.obj = obj
        return self.has_permission(request, view)


if 'rest_framework' in setting('INSTALLED_APPS'):
    from rest_framework.permissions import BasePermission

    class MightyPermissionDrf(BasePermission, MightyPermission):
        def has_permission(self, request, view):
            self.request = request
            self.view = view
            return self.check_permission()

        def has_object_permission(self, request, view, obj):
            self.obj = obj
            return self.has_permission(request, view)
