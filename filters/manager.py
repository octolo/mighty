from django.core.exceptions import PermissionDenied
from django.http import QueryDict

from mighty.applications.logger import EnableLogger


class FiltersManager(EnableLogger):
    cache_filters = None
    request = None
    data_load = None
    filter_post_enable = False

    def __init__(self, *args, **kwargs):
        self.flts = kwargs.get('flts', [])
        self.mandatories = kwargs.get('mandatories', [])
        self.filter_post_enable = kwargs.get('filter_post_enable', False)

    def check_mandatories(self, request):
        return all(k in self.get_data(request) for k in self.mandatories)

    def get_data(self, request, force=False):
        if not self.data_load or force:
            self.data_load = QueryDict('', mutable=True)
            self.request = request
            if hasattr(request, 'GET'):
                self.data_load.update(request.GET)
            if hasattr(request, 'POST') and self.filter_post_enable:
                if request.POST:
                    self.data_load.update(request.POST)
                elif hasattr(request, 'data'):
                    self.data_load.update(request.data)
        return self.data_load

    def params(self, request):
        if self.check_mandatories(request):
            return self.get_filters(request)
        raise PermissionDenied

    def get_filter(self, param, value):
        try:
            flt = next(x for x in self.flts if param in x.params_choices)
            if self.request.user.is_authenticated:
                return flt.sql(
                    {param: value}, user=self.request.user, bdata=self.data
                )
            return flt.sql({param: value}, bdata=self.data)
        except StopIteration:
            return None

    def get_filters(self, request):
        if not self.cache_filters:
            self.cache_filters = []
            self.data = list(self.get_data(request).lists())
            for param, value in self.data:
                flt = self.get_filter(param, value)
                if flt:
                    self.cache_filters.append(flt)
        self.cache_filters += (f.sql() for f in self.flts if f.default_value)
        return self.cache_filters

    def add(self, id_, filter_):
        self.flts[id_] = filter_
