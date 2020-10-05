from django.db.models import Q
from mighty import Verify
from mighty.functions import make_searchable, test, get_logger
from mighty.apps import MightyConfig

from functools import reduce
import logging, operator, uuid

logger = logging.getLogger(__name__)
SEPARATOR = MightyConfig.Interpreter._split

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

    #################
    # Verify
    #################
    def verify_field(self):
        if not self.field:
            msg = "field can't be empty!"
            logger.debug('filter %s: %s' % (self.id, msg))
            return msg

    def used(self):
        return True

    def used(self):
        return True

    #################
    # Dependency
    #################
    def get_dependencies(self):
        return reduce(operator.and_, [dep.sql(self.request) for dep in self.dependencies]) if self.dependencies else False

    ################
    # Value
    ################
    def get_value(self):
        return self.value

    ###############
    # Sql
    ##############
    def get_Q(self):
        return Q(**{self.field+self.mask: self.get_value(self.field)})

    def sql(self, request=None, *args, **kwargs):
        self.request = request
        self.method = kwargs.get('method', 'GET')
        self.method_request = kwargs.get('method_request', getattr(self.request, self.method))
        if self.verify() and self.used():
            dep = self.get_dependencies()
            sql = self.get_Q()
            return dep.add(sql, Q.AND) if dep and sql else sql
        return Q()

class ParamFilter(Filter):
    def __init__(self, id, request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.param = kwargs.get('param', self.id)

    def used(self):
        return True if self.method_request.get(self.param, False) else False

    def verify_param(self):
        if not self.param:
            return "param can't be empty!"

    def get_value(self, field):
        return self.method_request.get(self.param)

class ParamChoicesFilter(ParamFilter):
    def __init__(self, id, request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.choices = kwargs.get('choices')
        self.mask = kwargs.get('mask', '__iexact')

    def verify_param(self):
        if not self.choices or type(self.choices) != list:
            return "choices can't be empty and must be a list of choices"

    def get_value(self, field):
        print(self.choices)
        value = super().get_value(field)
        return value if value in self.choices else False

class ParamMultiChoicesFilter(ParamFilter):
    def __init__(self, id, request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.choices = kwargs.get('choices')
        self.mask = kwargs.get('mask', '__in')

    def verify_param(self):
        if not self.choices or type(self.choices) != list:
            return "choices can't be empty and must be a list of choices"

    def get_value(self, field):
        print([value for value in super().get_value(field).split(SEPARATOR) if value in self.choices])
        return [value for value in super().get_value(field).split(SEPARATOR) if value in self.choices]

class MultiParamFilter(ParamFilter):
    def __init__(self, id, request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.mask = kwargs.get('mask', '__icontains')

    def get_value(self):
        return super().get_value().split(SEPARATOR)

    def get_Q(self):
        return reduce(self.operator, [Q(**{self.field+self.mask: value }) for value in self.get_value(self.field)])

class SearchFilter(ParamFilter):
    def __init__(self, id='search', request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.mask = kwargs.get('mask', '__icontains')
        self.param = kwargs.get('param', self.id)
        self.field = self.prefix + kwargs.get('field', 'search')

    def get_value(self, field):
        return ['_'+value for value in super().get_value(field).split(SEPARATOR)]

    def get_Q(self):
        return reduce(self.operator, [Q(**{self.field+self.mask: value }) for value in self.get_value(self.field)])

class BooleanParamFilter(ParamFilter):
    def get_value(self, field):
        value = super().get_value(field)
        return bool(int(value))

class FiltersManager:
    def __init__(self, flts=None):
        self.flts = flts if flts else {}
    
    def params(self, request):
        return [f.sql(request) for f in self.flts]

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
        self.filters = {fltr.id: fltr for fltr in kwargs.get(self.Param._filters, [])}
        self.tokens = self.Token._filter+self.Token._family+[self.Token._split, self.Token._or]
        self.include = self.execute(request.GET.get(self.Param._include, False))
        self.exclude = self.execute(request.GET.get(self.Param._exclude, False))
        self.order = kwargs.get('order', False)
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

    def get_filter(self):
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
        #if self.distinct:
        #    #if self.qdistinct:
        #        #queryset = queryset.filter(id__in=queryset.order_by(*self.qdistinct).distinct(*self.qdistinct).values("id"))
        #    #if self.fdistinct:
        #        #queryset = queryset.order_by(*self.fdistinct).distinct(*self.fdistinct)
        #    #if self.distinct:
        #    if type(self.distinct) == bool:
        #        self.queryset = self.queryset.distinct()
        #    elif type(self.distinct) == list:
        #        self.queryset = self.queryset.distinct(*self.distinct)
        if self.order:
            self.queryset = self.queryset.order_by(*self.order)
        return self.queryset
