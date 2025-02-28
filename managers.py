import operator
from functools import reduce


class RequestManager:
    queryset = None
    request = None

    class Config:
        filters = False
        url_filters = False
        method = 'GET'

    def __init__(self, queryset, request, *args, **kwargs):
        self.filters = []
        self.queryset = queryset
        self.request = request
        self.Config.method = kwargs.get('method', self.Config.method)
        self.Config.filters = kwargs.get('filters', self.Config.filters)
        self.Config.url_filters = kwargs.get('url_filters', self.Config.url_filters)

    def add_filter(self, filtr):
        self.filters.append(filtr)

    def objects(self, request, op=operator.and_):
        filters = reduce(op, (filtr.F(request) for filtr in self.filters if filtr.F(request)))
        return self.queryset.filter(filters)
