from django.db.models import Q

class Filter:
    field = None
    way = ''
    mask = ''
    rules = None
    common_fields = {}

    def __init__(self, *args, **kwargs):
        self.field = kwargs.get('field', self.field)
        self.way = kwargs.get('way', self.way)
        self.mask = kwargs.get('mask', self.mask)
        self.rules = kwargs.get('rules', self.rules)

    def check(self, request, rules):
        return request.get(self.field)

    def F(self, request, rules=None):
        value = self.check(request, rules) if rules else self.check(request, self.rules)
        return Q(**{'%s%s%s' % (self.way, self.field, self.mask): value}) if value else False

class BooleanFilter(Filter):
    def check(self, request, rules):
        return bool(int(request.get(self.field)))

class ChoicesFilter(Filter):
    mask = '__iexact'

    def get(self, request, rules):
        field = request.get(self.field)
        return self.definition(field) if all(v in v for r in rules) or field in rules else False

    def definition(self, value):
        if type(value) == list: self.mask = '__in'
        return super().definition(value)