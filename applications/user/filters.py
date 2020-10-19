from mighty.filters import ParamMultiChoicesFilter


class SearchByGender(ParamMultiChoicesFilter):
    def __init__(self, id='gender', request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.choices = ['W', 'M']

    #def get_Q(self, exclude=False):
    #    theq = super().get_Q(exclude)
    #    print(theq)
    #    return theq