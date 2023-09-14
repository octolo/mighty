from django.db.models import Q
from mighty import Verify
from mighty.functions import make_float, make_int
from mighty.apps import MightyConfig

from functools import reduce
from datetime import timedelta, datetime
import operator, uuid, re

SEPARATOR = MightyConfig.Interpreter._split
NEGATIVE = MightyConfig.Interpreter._negative

class Filter(Verify):
    default_value = False
    is_array = False
    param_used = None
    delimiter = None
    regex_delimiter = None
    user = None
    extend = ()
    or_extend = ()
    and_extend = ()

    def __init__(self, id, *args, **kwargs):
        self.id = id if id else str(uuid.uuid4())
        self.operator = kwargs.get('operator', operator.and_)
        self.dependencies = kwargs.get('dependencies', [])
        self.mask = kwargs.get('mask', '')
        self.rmask = kwargs.get('rmask', '')
        self.param = kwargs.get('param', self.id)
        self.prefix = kwargs.get('prefix', '')
        self.field = kwargs.get('field', self.id)
        self.value = kwargs.get('value')
        self.choices = kwargs.get('choices')
        self.extend = kwargs.get('extend', self.extend)
        self.or_extend = kwargs.get('or_extend', self.or_extend)
        self.and_extend = kwargs.get('and_extend', self.and_extend)
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

    def get_rmask(self):
        return '__in' if self.is_array and not self.rmask else self.rmask

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
        return self.param if self.request and self.request.get(self.param, False) else False

    @property
    def is_negative(self):
        return self.negative_param if self.request and self.request.get(self.negative_param, False) else False

    @property
    def is_array_positive(self):
        return self.positive_array_param if self.request and self.request.get(self.positive_array_param, False) else False

    @property
    def is_array_negative(self):
        return self.negative_array_param if self.request and self.request.get(self.negative_array_param, False) else False

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
        if self.request:
            values = []
            if self.delimiter:
                for value in self.request.get(self.param_used):
                    if self.is_array:
                        for value in  self.request.get(self.param_used):
                            values += value.split(self.delimiter)
                    else:
                        values += self.request.get(self.param_used).split(self.delimiter)
                return values
            elif self.regex_delimiter:
                for value in self.request.get(self.param_used):
                    if value:
                        values += re.split(self.regex_delimiter, value)
                return values
            elif self.is_array:
                return self.request.get(self.param_used)
            return self.request.get(self.param_used)[0]
        return None

    def get_value_or_default(self):
        return self.get_value() or None

    def format_value(self):
        return self.get_value()

    def get_rfield(self):
        return self.prefix+self.field+self.get_rmask()

    def get_field(self):
        return self.prefix+self.field+self.get_mask()

    def get_field_extend(self, ext):
        return self.prefix+ext+self.get_mask()

    def extend_value(self):
        values = self.get_value()
        return [value for value in values]

    def get_orQ(self):
        if len(self.or_extend):
            return reduce(operator.or_, [self.usedQ(**{self.get_field_extend(ext): value}) for value in self.extend_value()
                for ext in self.or_extend])
        return Q()

    def get_andQ(self):
        if len(self.and_extend):
            return reduce(operator.and_, [self.usedQ(**{self.get_field_extend(ext): value}) for value in self.extend_value()
                for ext in self.and_extend])
        return Q()

    ###############
    # Sql
    ##############
    def usedQ(self, **kwargs):
        return ~Q(**kwargs) if self.is_negative or self.is_array_negative else Q(**kwargs)

    def get_Q(self):
        theQ = Q(**{self.get_field(): self.format_value()})
        return ~theQ if self.is_negative or self.is_array_negative else theQ

    def sql(self, request=None, *args, **kwargs):
        self.request = request
        self.data = kwargs.get('bdata')
        self.user = kwargs.get('user')
        if (self.verify() and self.used) or self.default_value:
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
        self.mask = kwargs.get('mask', '')
        self.fields = kwargs.get('fields', [])

    def get_value(self):
        return super().get_value().split(SEPARATOR)

    def fieldQ(self):
        return reduce(self.operator, [self.usedQ(**{self.get_field(): value }) for value in self.get_value()])

    def fieldsQ(self):
        return reduce(self.operator, [self.usedQ(**{self.get_field_extend(f): value}) for value in self.get_value()
            for f in self.fields])

    def get_Q(self):
        theQ = self.fieldsQ() if len(self.fields) else self.fieldQ()
        return theQ

class SearchFilter(ParamFilter):
    regex_delimiter = r'[;,\s]\s*'
    startw = ''

    def __init__(self, id='search', request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.mask = kwargs.get('mask', '__icontains')
        self.startw = kwargs.get('startw', '_')
        self.extstartw = kwargs.get('extstartw', '')

    def extend_value(self):
        values = super().get_value()
        return [self.extstartw+value for value in values]

    def get_mask(self):
        return self.mask

    def get_value(self):
        values = super().get_value()
        return [self.startw+value for value in values]

    def get_Q(self):
        values = self.get_value()
        if len(values):
            searchQ = reduce(self.operator, [self.usedQ(**{self.get_field(): value }) for value in values])
            test = (searchQ|self.get_andQ())|self.get_orQ()
            print(test)
            return test
        return Q()

class BooleanParamFilter(ParamFilter):
    enable_false = False

    def __init__(self, id, request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.enable_false = kwargs.get('enable_false', '')

    def get_mask(self):
        return self.mask

    def get_value(self):
        value = super().get_value()
        print("bool", value)
        if type(value).__name__ == "str":
            return True if value in ("true", "1") else False
        return bool(int(value))

    def get_Q(self):
        if self.enable_false or self.get_value():
            return super().get_Q()

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

class DatePastFilter(BooleanParamFilter):
    def __init__(self, id='coming', request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.field = kwargs.get('field', 'date')
        self.mask = kwargs.get('mask', '__gte')

    def get_Q(self):
        value = self.get_value()
        return Q(**{self.get_field(): datetime.today()})

class DateComingFilter(BooleanParamFilter):
    def __init__(self, id='coming', request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.field = kwargs.get('field', 'date')
        self.mask = kwargs.get('mask', '__gte')

    def get_Q(self):
        value = self.get_value()
        return Q(**{self.get_field(): datetime.today()})

class DatePastFilter(DateComingFilter):
    def __init__(self, id='past', request=None, *args, **kwargs):
        super().__init__(id, request, *args, **kwargs)
        self.mask = kwargs.get('mask', '__lt')
