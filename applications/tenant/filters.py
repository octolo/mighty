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

class IsMe(filters.BooleanParamFilter):
    def __init__(self, id='isme', request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.field = kwargs.get('field', 'tenant__user')

    def get_Q(self, exclude=False):
        value = self.get_value(exclude)
        return Q(**{self.field: self.request.user})

    
