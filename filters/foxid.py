from mighty.apps import MightyConfig
from functools import reduce
from datetime import timedelta
import operator

class Foxid:
    filters = None
    include = None
    excludes = None
    order = None
    distinct = None
    order_enable = False
    order_base = []

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
        self.order_base = kwargs.get('order_base', [])
        self.distinct = kwargs.get('distinct', False)
        self.order_enable = kwargs.get('order_enable', False)
        self.separator = self.Token._split
        self.negative = self.Token._negative

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
        if self.order:
            args += [o.replace('.', '__') for o in self.order.split(self.separator)]
        args_base = [arg.replace("-", "") for arg in args]
        if len(self.order_base):
            for ord_base in self.order_base:
                if ord_base.replace("-", "") not in args_base:
                    args.append(ord_base)
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
        if self.order_enable and self.order_by():
            self.queryset = self.queryset.order_by(*self.order_by())
        return self.queryset
