from django.db.models import Q
from mighty import Verify
from mighty.functions import make_searchable, test, get_logger
from functools import reduce
import operator

SEPARATOR = ','
class Filter(Verify):
    def __init__(self, request, *args, **kwargs):
        self.request = request
        self.method = kwargs.get('method', 'GET')
        self.mrequest = getattr(request, self.method)
        self.operator = kwargs.get('operator', operator.and_)
        self.mask = kwargs.get('mask', '')
        self.fields = kwargs.get('fields')
        self.value = kwargs.get('value')
        self.dependencies = {}
        self.verify()

    #################
    # Verify
    #################
    def verify_fields(self):
        if not self.fields:
            return "fields can't be empty!"

    #################
    # Dependency
    #################
    def has_dependency(self):
        return len([param for param, data in self.dependencies.items() if self.mrequest.get(param)])

    def add_dependency(self, param, way, mask=''):
        self.dependencies.update({param: [way, mask]})

    def get_dependencies(self):
        return reduce(
            operator.and_, 
            (Q('%s%s' % (data[0], data[1]), self.mrequest.get(param)) for param,data in self.dependencies.items() if self.mrequest.get(param))
        ) if self.dependencies and type(self.dependencies) == dict else False

    ################
    # Value
    ################
    def get_value(self, field):
        return self.value

    ###############
    # Sql
    ##############
    def sql(self):
        value, sql = self.get_value(), False
        if value:
            dep = self.get_dependencies()
            sql = reduce(
                self.operator,
                (Q(field+self.mask, self.get_value(field)) for field in self.fields)
            ) if type(self.fields) == list else Q(self.fields+self.mask, self.get_value(self.fields))
            sql = dep.add(sql, Q.AND) if dep and sql else sql
        return sql

class ParamFilter(Filter):
    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kargs)
        self.param = kwargs.get('param'), param, choices, 

    def verify_param(self):
        if not self.param:
            return "param can't be empty!"

    def get_value(self, field):
        return self.mrequest.get(self.param)

class ParamChoicesFilter(ParamFilter):
    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kargs)
        self.choices = kwargs.get('choices')
        self.mask = '__iexact'

    def verify_param(self):
        if not self.choices or type(self.choices) != list:
            return "choices can't be empty and must be a list of choices"

    def get_value(self):
        value = super().get_value()
        return value if value in self.choices else False

class ParamMultiChoicesFilter(ParamFilter):
    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kargs)
        self.choices = kwargs.get('choices')
        self.mask = '__in'

    def verify_param(self):
        if not self.choices or type(self.choices) != list:
            return "choices can't be empty and must be a list of choices"

    def get_value(self):
        values = super().get_value().split(SEPARATOR)
        return [value for value in values if value in self.choices]

#keywords = ['filter', 'exclude', 'distinct', 'order', 'limit', 'offset']
## filter=(~,f(1,'tata'),f(3),(f(2),f(4)),f(5,'trublion,trashconnector'))&extra=f(12,'2018')
#class ParserFilter:
#    def __init__(self, request, *args, **kwargs):
#        self.request = request
#        self.keywords = kwargs.get('keywords', keywords)
#        self.separator = kwargs.get('separator', separator)