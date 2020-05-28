from django.db.models import Q
from mighty.functions import make_searchable, test, get_logger
from functools import reduce
import operator

logger = get_logger()

class RequestManager:
    model = None
    request = None

    class Config:
        filters = False
        url_filters = False
        method = 'GET'

    def __init__(self, request, *args, **kwargs):
        self.Config.method = kwargs.get('method', self.Config.method)
        self.Config.filters = kwargs.get('filters', self.Config.filters)
        self.Config.url_filters = kwargs.get('url_filters', self.Config.url_filters)
        self.request = request