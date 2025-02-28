from django.db.models import Q

from mighty import filters


class SearchByGroupUid(filters.ParamFilter):
    def __init__(self, id='group', request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.field = kwargs.get('field', 'group__uid')


class SearchByRoleUid(filters.ParamFilter):
    def __init__(self, id='role', request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.field = kwargs.get('field', 'roles__uid')


class SearchBySettingUid(filters.ParamFilter):
    def __init__(self, id='role', request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.field = kwargs.get('field', 'settings__uid')

    def get_Q(self):
        value = self.get_value()
        return super().get_Q() if value else Q()


class IsMe(filters.BooleanParamFilter):
    def __init__(self, id='isme', request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.field = kwargs.get('field', 'tenant__user')

    def get_Q(self, exclude=False):
        value = self.get_value(exclude)
        return Q(**{self.field: self.request.user})
