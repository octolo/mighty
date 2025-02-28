from mighty.filters import ParamMultiChoicesFilter


class Alpha2(ParamMultiChoicesFilter):
    def __init__(self, id='nat_alpha2', request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.field = kwargs.get('field', 'alpha2')


class Alpha3(ParamMultiChoicesFilter):
    def __init__(self, id='nat_alpha3', request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.field = kwargs.get('field', 'alpha3')


class Numeric(ParamMultiChoicesFilter):
    def __init__(self, id='nat_numeric', request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.field = kwargs.get('field', 'numeric')
