from django.db.models import Q
from django.http import QueryDict
from django.core.exceptions import PermissionDenied

from mighty import Verify
from mighty.functions import make_searchable, test, get_logger, make_float, make_int
from mighty.apps import MightyConfig

from functools import reduce
from datetime import timedelta
import logging, operator, uuid, re

logger = logging.getLogger(__name__)
SEPARATOR = MightyConfig.Interpreter._split
NEGATIVE = MightyConfig.Interpreter._negative

class Filter(Verify):
    is_array = False
    param_used = None
    delimiter = None
    regex_delimiter = None
    user = None

    def __init__(self, id, *args, **kwargs):
        self.id = id if id else str(uuid.uuid4())
        self.operator = kwargs.get('operator', operator.and_)
        self.dependencies = kwargs.get('dependencies', [])
        self.mask = kwargs.get('mask', '')
        self.param = kwargs.get('param', self.id)
        self.prefix = kwargs.get('prefix', '')
        self.field = kwargs.get('field', self.id)
        self.value = kwargs.get('value')
        self.choices = kwargs.get('choices')
        self.params_choices = [
            self.param,
            self.negative_param,
            self.positive_array_param,
            self.negative_array_param,
        ]

    #################
    # Verify
    #################
    def verify_param(self):
        if not self.param:
            return "param can't be empty!"

    def verify_field(self):
        if not self.field:
            msg = "field can't be empty!"
            return msg

    def get_mask(self):
        return '__in' if self.is_array and not self.mask else self.mask

    #################
    # Param
    #################
    @property
    def negative_param(self, array=False):
        return NEGATIVE+self.param

    @property
    def positive_array_param(self):
        return self.param+'[]'

    @property
    def negative_array_param(self):
        return NEGATIVE+self.param+'[]'

    @property
    def is_positive(self):
        return self.param if self.request.get(self.param, False) else False

    @property
    def is_negative(self):
        return self.negative_param if self.request.get(self.negative_param, False) else False

    @property
    def is_array_positive(self):
        return self.positive_array_param if self.request.get(self.positive_array_param, False) else False
    
    @property
    def is_array_negative(self):
        return self.negative_array_param if self.request.get(self.negative_array_param, False) else False

    @property
    def used(self):
        if self.is_positive:
            self.param_used = self.is_positive
            return True
        elif self.is_negative:
            self.param_used = self.is_negative
            return True
        elif self.is_array_positive:
            self.param_used = self.is_array_positive
            self.is_array = True
            return True
        elif self.is_array_negative:
            self.param_used = self.is_array_negative
            self.is_array = True
            return True
        return False

    #################
    # Dependency
    #################
    def get_dependencies(self):
        return reduce(operator.and_, [dep.sql(self.request) for dep in self.dependencies]) if self.dependencies else False

    ################
    # Value
    ################
    def get_value(self):
        if self.delimiter:
            values = []
            for value in self.request.get(self.param_used):
                if self.is_array:
                    for value in  self.request.get(self.param_used):
                        values += value.split(self.delimiter)
                else:
                    values += self.request.get(self.param_used).split(self.delimiter)
            return values
        elif self.regex_delimiter:
            values = []
            for value in self.request.get(self.param_used):
                if value:
                    values += re.split(self.regex_delimiter, value)
            return values
        elif self.is_array:
            return self.request.get(self.param_used)
        return self.request.get(self.param_used)[0]

    def format_value(self):
        return self.get_value()

    def get_field(self):
        return self.prefix+self.field+self.get_mask()

    ###############
    # Sql
    ##############
    def get_Q(self):
        theQ = Q(**{self.get_field(): self.format_value()})
        return ~theQ if self.is_negative or self.is_array_negative else theQ

    def sql(self, request=None, *args, **kwargs):
        self.request = request
        self.data = kwargs.get('bdata')
        self.user = kwargs.get('user')
        if self.verify() and self.used:
            sql = self.get_Q()
            dep = self.get_dependencies()
            return dep.add(sql, Q.AND) if dep and sql else sql
        return Q()

class ParamFilter(Filter):
    pass

class ParamChoicesFilter(ParamFilter):
    def __init__(self, id, request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.choices_required = kwargs.get('choices_required', False)
        self.mask = kwargs.get('mask', '__iexact')

    def verify_param(self):
        if self.choices_required and (not self.choices or type(self.choices) != list):
            return "choices can't be empty and must be a list of choices"

    def get_value(self):
        value = super().get_value()
        if self.choices_required:
            return value if value in self.choices else False
        return value

class ParamMultiChoicesFilter(ParamFilter):
    def __init__(self, id, request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.mask = kwargs.get('mask', '__in')
        self.choices_required = kwargs.get('choices_required', False)

    def verify_param(self):
        if self.choices_required and (not self.choices or type(self.choices) != list):
            return "choices can't be empty and must be a list of choices"

    def get_value(self):
        values = super().get_value()
        if self.choices_required:
            if self.is_array:
                return [value for value in values if value in self.choices]
            return values if values in self.choices else None
        return [value for value in values]

class MultiParamFilter(ParamFilter):
    def __init__(self, id, request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.mask = kwargs.get('mask', '__icontains')

    def get_value(self):
        return super().get_value().split(SEPARATOR)

    def get_Q(self):
        if self.is_negative or self.is_array_negative:
            return reduce(self.operator, [~Q(**{self.get_field(): value }) for value in self.get_value()])
        return reduce(self.operator, [Q(**{self.get_field(): value }) for value in self.get_value()])

class SearchFilter(ParamFilter):
    regex_delimiter = r'[;,\s]\s*'
    startw = ''

    def __init__(self, id='search', request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.mask = kwargs.get('mask', '__icontains')
        self.startw = kwargs.get('startw', '_')

    def get_mask(self):
        return self.mask

    def get_value(self):
        values = super().get_value()
        return [self.startw+value for value in values]

    def get_Q(self):
        values = self.get_value()
        if len(values):
            if self.is_negative or self.is_array_negative:
                return reduce(self.operator, [~Q(**{self.get_field(): value }) for value in values])
            return reduce(self.operator, [Q(**{self.get_field(): value }) for value in values])
        return Q()

class BooleanParamFilter(ParamFilter):
    def get_mask(self):
        return self.mask

    def get_value(self):
        value = super().get_value()[0]
        return bool(int(value))

class FilterByGTEorLTE(ParamMultiChoicesFilter):
    def __init__(self, id='gtelte', request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.mask = kwargs.get('mask', '')
        self.is_int = kwargs.get('is_int', False)
        self.operator = operator.or_

    def get_field(self, value, field):
        if value[0:3] in ['gte', 'lte']:
            return self.prefix+field+'__gte' if value[0:3] == 'gte' else self.prefix+field+'__lte'
        elif value[0:2] in ['gt', 'lt']:
            return self.prefix+field+'__gt' if value[0:2] == 'gt' else self.prefix+field+'__lt'
        return self.prefix+field+self.mask

    def format_value(self, value):
        if self.is_int:
            return make_int(value)
        return make_float(value)

    def get_LTEGTE(self, field):
        theQ = []
        for value in self.get_value():
            if '-' in value:
                value = value.split('-')
                theQ.append(Q(**{
                    self.prefix+field+'__gte': self.format_value(value[0]), 
                    self.prefix+field+'__lte': self.format_value(value[1]) 
                }))
            else:
                theQ.append(Q(**{self.get_field(value, field): self.format_value(value) }))
        if self.is_negative or self.is_array_negative:
            return ~reduce(self.operator, theQ)
        return reduce(self.operator, theQ)

    def get_Q(self):
        return self.get_LTEGTE(self.field)

class FilterByYearDelta(FilterByGTEorLTE):
    def __init__(self, id='years', request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)

    def format_value(self, value):
        return timedelta(days=make_float(value)*MightyConfig.days_in_year)

class FiltersManager:
    cache_filters = None
    request = None
    data_load = None

    def __init__(self, *args, **kwargs):
        self.flts = kwargs.get('flts', [])
        self.mandatories = kwargs.get('mandatories', [])

    def check_mandatories(self, request):
        return all(k in self.get_data(request) for k in self.mandatories)
    
    def get_data(self, request, force=False):
        if not self.data_load or force:
            self.data_load = QueryDict('', mutable=True)
            self.request = request
            if hasattr(request, 'GET'):
                self.data_load.update(request.GET)
            if hasattr(request, 'POST'):
                if request.POST:
                    self.data_load.update(request.POST)
                elif hasattr(request, 'data'):
                    self.data_load.update(request.data)
        return self.data_load

    def params(self, request):
        if self.check_mandatories(request):
            return self.get_filters(request)
        raise PermissionDenied()

    def get_filter(self, param, value):
        try:
            flt = next(x for x in self.flts if param in x.params_choices)
            if self.request.user.is_authenticated:
                return flt.sql({param: value}, user=self.request.user, bdata=self.data)
            return flt.sql({param: value}, bdata=self.data)
        except StopIteration:
            return None

    def get_filters(self, request):
        if not self.cache_filters: 
            self.cache_filters = []
            self.data = list(self.get_data(request).lists())
            logger.info('URL data: %s' % self.data)
            for param, value in self.data:
                flt = self.get_filter(param, value)
                if flt: self.cache_filters.append(flt)
        #self.cache_filters = [f.sql(request) for f in self.flts if f.sql(request)]
        logger.info('Filter: %s' % self.cache_filters)
        return self.cache_filters

    def add(self, id_, filter_):
        self.flts[id_] = filter_

class Foxid:
    filters = None
    include = None
    excludes = None
    order = None
    distinct = None
    order_enable = True
    order_base = None

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
        self.order_base = kwargs.get('order_base', False)
        self.distinct = kwargs.get('distinct', False)

    def execute(self, input_str):
        if input_str:
            i = 0
            while i < len(input_str):
                char = input_str[i]
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
                            self.context.pop()
                            self.add_filter(self.get_filter_by_idandargs())

                        # closing family
                        elif char == self.Token._family[1] and self.context[-1] == self.Token._family[0]:
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

    def order_by(self):
        args = []
        args += self.order.replace('.', '__').split(SEPARATOR)
        args_base = [arg.replace("-", "") for arg in args]
        if self.order_base:
            ord_base = self.order_base.replace("-", "")
            if ord_base not in args_base:
                args.append(self.order_base)
        return args

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
        if self.order and self.order_enable:
            print(self.order_by())
            self.queryset = self.queryset.order_by(*self.order_by())
        return self.queryset
        #return [value for value in super().get_value().split(SEPARATOR)]