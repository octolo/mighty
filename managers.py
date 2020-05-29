from django.db.models import Q
from mighty.functions import make_searchable, test, get_logger
from functools import reduce
import operator

logger = get_logger()


class Filter:
    way = ''
    field = ''
    value = ''
    common_fields = {}

    def common(self):
        return [getattr(self, field)(field) for field in self.common_fields]

    def definition(self, value=None):
        return Q({'%s%s' % (self.way, self.field): value if value else self.value})

class RequestManager:
    model = None
    request = None

    class Config:
        filters = False
        url_filters = False
        method = 'GET'

    def __init__(self, *args, **kwargs):
        self.Config.method = kwargs.get('method', self.Config.method)
        self.Config.filters = kwargs.get('filters', self.Config.filters)
        self.Config.url_filters = kwargs.get('url_filters', self.Config.url_filters)
        self.arguments = args