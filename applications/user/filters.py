from mighty.filters import ParamMultiChoicesFilter

class SearchByGender(ParamMultiChoicesFilter):
    def __init__(self, id='gender', request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.choices = ['W', 'M']
