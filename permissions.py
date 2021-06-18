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


if 'rest_framework' in setting('INSTALLED_APPS'):
    from rest_framework.permissions import BasePermission
    base_action = ["list", "retrieve", "create", "update", "partial_update", "destroy"]
    base_permission = ["is_superuser", "is_staff", "is_me",]

    class MightyPermission(BasePermission):
        request = None
        view = None
        user = None
        model = None
        action_list = base_action
        check_list = base_permission
        check_retrieve = base_permission
        check_create = base_permission
        check_update = base_permission
        check_partial_update = base_permission
        check_destroy = base_permission
        check_others = base_permission

    """ Properties """
    @property
    def user(self):
        return request.user

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

    @property
    def is_me(self):
        raise NotImplementedError("Subclasses should implement is_me")
        
    """ Permissions by action """
    def can_list(self):
        return self.check_action("list")

    def can_retrieve(self):
        return self.check_action("retrieve")

    def can_create(self):
        return self.check_action("create")

    def can_update(self):
        return self.check_action("update")

    def can_partial_update(self):
        return self.check_action("partial_update")

    def can_destroy(self):
        return self.check_action("destroy")

    """ Check if action has permission """
    def can_check_action(self, action):
        check_action = getattr(self, "check_"+action)
        if len(check_action):
            return any([getattr(self, check) for check in check_action])
        else:
            return any([getattr(self, check) for check in self.check_others])

    """ Loop on permission action """
    def has_permission(self, request, view):
        self.request = request
        self.view = view
        if request.user.is_authenticated:
            for action in self.action_list:
                if callable(self, "can_"+action):
                    return getattr(self, action)()
        return False
