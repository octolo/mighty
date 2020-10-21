from django.db.models import Q

from mighty import Verify
from mighty.functions import make_searchable, test, get_logger, make_float
from mighty.apps import MightyConfig

from functools import reduce
from datetime import timedelta
import logging, operator, uuid

logger = logging.getLogger(__name__)
SEPARATOR = MightyConfig.Interpreter._split
NEGATIVE = MightyConfig.Interpreter._negative

class Filter(Verify):
    def __init__(self, id, *args, **kwargs):
        self.id = id if id else str(uuid.uuid4())
        self.operator = kwargs.get('operator', operator.and_)
        self.dependencies = kwargs.get('dependencies', [])
        self.mask = kwargs.get('mask', '')
        self.param = kwargs.get('param', self.id)
        self.prefix = kwargs.get('prefix', '')
        self.field = self.prefix + kwargs.get('field', self.id)
        self.value = kwargs.get('value')
        self.choices = kwargs.get('choices')

    #################
    # Verify
    #################
    def verify_field(self, exclude=False):
        if not self.field:
            msg = "field can't be empty!"
            logger.debug('filter %s: %s' % (self.id, msg))
            return msg

    def used(self, exclude=False):
        return True

    #################
    # Dependency
    #################
    def get_dependencies(self, exclude=False):
        return reduce(operator.and_, [dep.sql(self.request) for dep in self.dependencies]) if self.dependencies else False

    ################
    # Value
    ################
    def get_value(self, exclude=False):
        return self.value

    def format_value(self, value):
        return value

    def get_field(self, value):
        return self.field+self.mask

    ###############
    # Sql
    ##############
    def get_Q(self, exclude=False):
        value = self.get_value(exclude)
        return Q(**{self.get_field(value): self.format_value(value)})

    def sql(self, request=None, exclude=False, *args, **kwargs):
        self.request = request
        self.method = kwargs.get('method', 'GET')
        self.method_request = kwargs.get('method_request', getattr(self.request, self.method))
        if self.verify(exclude) and self.used(exclude):
            dep = self.get_dependencies(exclude)
            sql = self.get_Q(exclude)
            print(sql)
            return dep.add(sql, Q.AND) if dep and sql else sql
        return Q()

class ParamFilter(Filter):
    def used(self, exclude=False):
        if exclude:
            return True if self.method_request.get(NEGATIVE+self.param, False) else False
        return True if self.method_request.get(self.param, False) else False

    def verify_param(self, exclude=False):
        if not self.param:
            return "param can't be empty!"

    def get_value(self, exclude=False):
        param = NEGATIVE+self.param if exclude else self.param
        return self.method_request.get(param)

class ParamChoicesFilter(ParamFilter):
    def __init__(self, id, request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.choices_required = kwargs.get('choices_required', False)
        self.mask = kwargs.get('mask', '__iexact')

    def verify_param(self, exclude=False):
        if self.choices_required and (not self.choices or type(self.choices) != list):
            return "choices can't be empty and must be a list of choices"

    def get_value(self, exclude=False):
        value = super().get_value(exclude)
        if self.choices_required:
            return value if value in self.choices else False
        return value

class ParamMultiChoicesFilter(ParamFilter):
    def __init__(self, id, request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.choices_required = kwargs.get('choices_required', False)
        self.mask = kwargs.get('mask', '__in')

    def verify_param(self, exclude=False):
        if self.choices_required and (not self.choices or type(self.choices) != list):
            return "choices can't be empty and must be a list of choices"

    def get_value(self, exclude=False):
        values = super().get_value(exclude).split(SEPARATOR)
        if self.choices_required:
            return [value for value in values if value in self.choices]
        return [value for value in values]

class MultiParamFilter(ParamFilter):
    def __init__(self, id, request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.mask = kwargs.get('mask', '__icontains')

    def get_value(self):
        return super().get_value().split(SEPARATOR)

    def get_Q(self, exclude=False):
        return reduce(self.operator, [Q(**{self.get_field(value): value }) for value in self.get_value(exclude)])

class SearchFilter(ParamFilter):
    def __init__(self, id='search', request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.mask = kwargs.get('mask', '__icontains')

    def get_value(self, exclude=False):
        return ['_'+value for value in super().get_value(exclude).split(SEPARATOR)]

    def get_Q(self, exclude=False):
        return reduce(self.operator, [Q(**{self.get_field(value): value }) for value in self.get_value(exclude)])

class BooleanParamFilter(ParamFilter):
    def get_value(self, exclude=False):
        value = super().get_value(exclude)
        return bool(int(value))

class FilterByGTEorLTE(ParamMultiChoicesFilter):
    def __init__(self, id='gtelte', request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.mask = kwargs.get('mask', '')
        self.operator = operator.or_

    def get_field(self, value):
        if value[0:3] in ['gte', 'lte']:
            return self.field+'__gte' if value[0:3] == 'gte' else self.field+'__lte'
        elif value[0:2] in ['gt', 'lt']:
            return self.field+'__gt' if value[0:2] == 'gt' else self.field+'__lt'
        return self.field+self.mask

    def format_value(self, value):
        return make_float(value)

    def get_Q(self, exclude=False):
        theQ = []
        for value in self.get_value(exclude):
            if '-' in value:
                value = value.split('-')
                theQ.append(Q(**{
                    self.field+'__gte': self.format_value(value[0]), 
                    self.field+'__lte': self.format_value(value[1]) 
                }))
            else:
                theQ.append(Q(**{self.get_field(value): self.format_value(value) }))
        return reduce(self.operator, theQ)

class FilterByYearDelta(FilterByGTEorLTE):
    def __init__(self, id='years', request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)

    def format_value(self, value):
        return timedelta(days=make_float(value)*MightyConfig.days_in_year)

class FiltersManager:
    def __init__(self, flts=None):
        self.flts = flts if flts else {}
    
    def params(self, request, exclude=False):
        return self.get_filters(request, exclude)

    def get_filters(self, request, exclude=False):
        filters = [f.sql(request, exclude) for f in self.flts if f.sql(request, exclude)]
        return filters

    def add(self, id_, filter_):
        self.flts[id_] = filter_

class Foxid:
    filters = None
    include = None
    excludes = None
    order = None
    distinct = None

    class Param:
        _filters = 'f'
        _include = 'i'
        _exclude = 'x'
        _distinct = 'd'
        _order = 'o'

    class Token(MightyConfig.Interpreter):
        pass

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
        self.method_request = getattr(self.request, self.method)
        self.filters = {fltr.id: fltr for fltr in kwargs.get(self.Param._filters, [])}
        self.tokens = self.Token._filter+self.Token._family+[self.Token._split, self.Token._or]
        self.include = self.execute(request.GET.get(self.Param._include, False))
        self.exclude = self.execute(request.GET.get(self.Param._exclude, False))
        self.order = self.method_request.get(self.Param._order, kwargs.get('order', False))
        self.distinct = kwargs.get('distinct', False)

    def execute(self, input_str):
        if input_str:
            i = 0
            while i < len(input_str):
                char = input_str[i]
                logger.debug('WHILE compiled: %s' % self.compiled)
                logger.debug('WHILE context: %s' % self.context)
                logger.debug('WHILE idorarg: %s' % self.idorarg)
                logger.debug('WHILE filter_idandargs: %s' % self.filter_idandargs)
                logger.debug('WHILE char: %s' % char)
                i += 1
                if char in self.tokens:

                    # if filter starting
                    if char == self.Token._filter[0]:
                        # not already in filter
                        if not len(self.context):
                            self.context.append(self.Token._filter[0])
                        # if filter in family
                        elif self.context[-1] == self.Token._family[0]:
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
                            self.add_filter(self.get_filter_by_idandargs())

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

                # No token
                else:
                    if not self.context:
                        raise SyntaxError('request interepreter need a starting condition')
                    else:
                        self.concate_idorarg(char)

            if self.compiled:
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
        if fltr:
            self.families[-1].append(fltr) if len(self.families) else self.compiled.append(fltr)

    def get_filter_by_idandargs(self):
        if len(self.filter_idandargs) and self.filter_idandargs[0] in self.filters:
            fltr = self.filters[self.filter_idandargs[0]]
            fltr.request = self.request
            args = self.filter_idandargs[1] if len(self.filter_idandargs) == 2 else self.Token._split.join(self.filter_idandargs[1:])
            self.filter_idandargs = []
            return fltr.sql(self.request, method_request={fltr.param: args})
        return False

    def ready(self):
        if self.include:
            self.queryset = self.queryset.filter(self.include)
        if self.exclude:
            self.queryset = self.queryset.exclude(self.exclude)
        if self.distinct:
            if type(self.distinct) == str and self.distinct == 'auto':
                queryset = queryset.filter(id__in=queryset.distinct(*self.qdistinct).values("id"))
            elif type(self.distinct) == bool:
                self.queryset = self.queryset.distinct()
            elif type(self.distinct) == list:
                self.queryset = self.queryset.distinct(*self.distinct)
        if self.order:
            self.queryset = self.queryset.order_by(*self.order.replace('.', '__').split(SEPARATOR))
        return self.queryset
        #return [value for value in super().get_value(exclude).split(SEPARATOR)]