from django.db.models import Q
from mighty import Verify
from mighty.functions import make_searchable, test, get_logger

from functools import reduce
import logging, operator

logger = logging.getLogger(__name__)
SEPARATOR = ','

class Filter(Verify):
    def __init__(self, id, request=None, *args, **kwargs):
        self.id = id
        self.request = request
        self.param = kwargs.get('param')
        self.method = kwargs.get('method', 'GET')
        self.operator = kwargs.get('operator', operator.and_)
        self.mask = kwargs.get('mask', '')
        self.fields = kwargs.get('fields')
        self.value = kwargs.get('value')
        self.dependencies = {}

    #################
    # Verify
    #################
    def verify_fields(self):
        if not self.fields:
            return "fields can't be empty!"

    def used(self):
        return True

    #################
    # Dependency
    #################
    def has_dependency(self):
        return len([param for param, data in self.dependencies.items() if self.method_request.get(param)])

    def add_dependency(self, param, way, mask=''):
        self.dependencies.update({param: [way, mask]})

    def get_dependencies(self):
        return reduce(
            operator.and_, 
            (Q('%s%s' % (data[0], data[1]), self.request.get(param)) for param,data in self.dependencies.items() if self.request.get(param))
        ) if self.dependencies and type(self.dependencies) == dict else False

    ################
    # Value
    ################
    def get_value(self, field):
        return self.value

    ###############
    # Sql
    ##############
    def multi_field(self):
        return reduce(self.operator, [Q(**{field+self.mask: self.get_value(field)}) for field in self.fields])

    def one_field(self):
        return Q(**{self.fields+self.mask: self.get_value(self.fields)})

    def sql(self, method_request=None):
        self.method_request = method_request if method_request else getattr(self.request, self.method)
        self.verify()
        if self.used():
            #dep = self.get_dependencies()
            sql = self.multi_field() if type(self.fields) == list else self.one_field()
            #return dep.add(sql, Q.AND) if dep and sql else sql
            return sql
        return Q()


class ParamFilter(Filter):
    def __init__(self, id, request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.param = kwargs.get('param')#, param, choices, 

    def used(self):
        return True if self.method_request.get(self.param, False) else False

    def verify_param(self):
        if not self.param:
            return "param can't be empty!"
            
    def get_value(self, field):
        return self.method_request.get(self.param)

class ParamChoicesFilter(ParamFilter):
    def __init__(self, id, request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kargs)
        self.choices = kwargs.get('choices')
        self.mask = '__iexact'

    def verify_param(self):
        if not self.choices or type(self.choices) != list:
            return "choices can't be empty and must be a list of choices"

    def get_value(self, field):
        value = super().get_value(field)
        return value if value in self.choices else False

class ParamMultiChoicesFilter(ParamFilter):
    def __init__(self, id, request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.choices = kwargs.get('choices')
        self.mask = '__in'

    def verify_param(self):
        if not self.choices or type(self.choices) != list:
            return "choices can't be empty and must be a list of choices"

    def get_value(self, field):
        values = super().get_value(field).split(SEPARATOR)
        return [value for value in values if value in self.choices]

class MultiParamFilter(ParamFilter):
    def __init__(self, id, request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.mask = kwargs.get('mask', '__icontains')

    def get_value(self, field):
        return super().get_value(field).split(SEPARATOR)

    def one_field(self):
        return reduce(self.operator, [Q(**{self.fields+self.mask: value }) for value in self.get_value(self.fields)])

class BooleanParamFilter(ParamFilter):
    def get_value(self, field):
        value = super().get_value(field)
        return bool(int(value))

class RequestInterpreter:
    filters = None
    include = None
    excludes = None
    distinct = None
    order = None

    class Param:
        _filters = 'flts'
        _include = 'incd'
        _exclude = 'excd'
        _distinct = 'dstc'
        _order = 'ordr'

    class Token:
        _idorarg = 'IDorARG'
        _filter = ['f', '(', ')']
        _family = ['(', ')']
        _or = '~'
        _split= ','
        _all_ = _filter+_family+[_split, _or]

    def __init__(self, queryset, request, *args, **kwargs):
        self.queryset = queryset
        self.request = request
        self.compiled = []
        self.families = []
        self.context = []
        self.filter_idandargs = []
        self.operators = []
        self.idorarg = ''
        self.method = kwargs.get('method', 'GET')
        self.filters = {fltr.id: fltr for fltr in kwargs.get(self.Param._filters, [])}
        self.include = self.execute(request.GET.get(self.Param._include, False))
        self.exclude = self.execute(request.GET.get(self.Param._exclude, False))

    def execute(self, input_str):
        if input_str:
            i = 0
            while i < len(input_str):
                char = input_str[i]
                i += 1
                if char in self.Token._all_:

                    # if filter starting
                    if char == self.Token._filter[0]:
                        # not already in filter
                        if not len(self.context) or self.context[-1] not in [self.Token._filter[0], self.Token._filter[0]+self.Token._filter[1]]:
                            self.context.append(self.Token._filter[0])
                        else:
                            # ID or ARG
                            self.concate_idorarg(char)
                    
                    # opening form
                    elif char in [self.Token._filter[1], self.Token._family[0]]:

                        # opening filter
                        if len(self.context) and self.context[-1] == self.Token._filter[0] and char == self.Token._filter[1]:
                            self.context[-1] = self.Token._filter[0] + self.Token._filter[1]

                        # opening clause family
                        elif char == self.Token._family[0]:
                            self.context.append(self.Token._family[0])
                            self.families.append([])

                    # closing form
                    elif char in [self.Token._filter[2], self.Token._family[1]]:
                        if len(self.context) and self.context[-1] == self.Token._idorarg:
                            self.add_idorarg()

                        # closing filter
                        if char == self.Token._filter[2] and self.context[-1] == self.Token._filter[0]+self.Token._filter[1]:
                            logger.warning('close filter')
                            self.context.pop()
                            self.add_filter(self.get_filter())

                        # closing family
                        elif char == self.Token._family[1] and self.context[-1] == self.Token._family[0]:
                            logger.warning('close family')
                            self.add_filter(reduce(self.operators.pop() if len(self.operators) else operator.and_, self.families.pop()))
                            self.context.pop()

                    # split id, arg, family or filter
                    elif char == self.Token._split:
                        # if context is and id or an argument
                        if len(self.context) and self.context[-1] == self.Token._idorarg:
                            self.add_idorarg()
                            
                    # if family operator
                    elif char == self.Token._or:
                        self.operators.append(operator.or_)

                # ID or ARG
                else:
                    self.concate_idorarg(char)

            self.compiled = reduce(self.operators.pop() if len(self.operators) else operator.and_, self.compiled)
            logger.info('END compiled: %s' % self.compiled)
            logger.info('END context: %s' % self.context)
            logger.info('END idorarg: %s' % self.idorarg)
            logger.info('END filter_idandargs: %s' % self.filter_idandargs)
            logger.info('END char: %s' % char)

        if len(self.context):
            raise SyntaxError('invalid syntax of the request interpreter')

        compiled, self.compiled = self.compiled, []
        return compiled if compiled else False

    def add_idorarg(self):
        self.filter_idandargs.append(self.idorarg)
        self.context.pop()
        self.idorarg = ''

    def concate_idorarg(self, char):
        if self.context[-1] != self.Token._idorarg: 
            self.context.append(self.Token._idorarg)
        self.idorarg+=char

    def add_filter(self, fltr):
        self.families[-1].append(fltr) if len(self.families) else self.compiled.append(fltr)

    def get_filter(self):
        fltr = self.filters[self.filter_idandargs[0]]
        fltr.request = self.request
        args = self.filter_idandargs[1] if len(self.filter_idandargs) == 2 else self.Token._split.join(self.filter_idandargs[1:])
        self.filter_idandargs = []
        return fltr.sql({fltr.param: args})

    def ready(self):
        if self.include:
            self.queryset = self.queryset.filter(self.include)
        if self.exclude:
            self.queryset = self.queryset.exclude(self.exclude)
        return self.queryset