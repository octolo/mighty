from mighty.filters import ParamMultiChoicesFilter


class SearchByGender(ParamMultiChoicesFilter):
    def __init__(self, id='gender', request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.choices = ['W', 'M']

    def format_value(self, value):
        if type(value) == list:
            return [v.upper() for v in value]
        return value.upper()

    #def get_Q(self, exclude=False):
    #    theq = super().get_Q(exclude)
    #    print(theq)
    #    return theq