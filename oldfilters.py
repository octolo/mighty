from django.db.models import Q
from mighty.functions import make_searchable, test, get_logger
from functools import reduce
import operator

logger = get_logger()

class Filter:
    class Separators:
        _category = ":"
        _marker = "--"
        _operator = "~"
        _multiseparator = "!"
        _separator = " "
        _key = "=="
        _range = "-"
        _in = ","
        _list = ","
        _safe = "$"
        _pos = ":"

    class Operators:
        authorized = ["range", "in", "list", "bool"]

    class Arguments:
        filters = "filters"
        excludes = "excludes"
        distinct = "distinct"
        qdistinct = "qdistinct"
        fdistinct = "fdistinct"
        limit = "limit"
        order = "order"

    def get_queryset(self):
        return self.queryset if self.queryset else self.model.objects

    def __init__(self, request, model, method="GET"):
        self.method = method
        #self.model = model
        self.queryset = None
        #self.filters = []
        #self.excludes = []
        self.distinct = False
        self.qdistinct = False
        self.fdistinct = False
        self.limit = False
        self.order = False
        self.nparams = {}
        self.model = model
        self.request = request
        if hasattr(request, method): self.args = getattr(request, method)
        self.filters = self.parser(self.Arguments.filters)
        self.excludes = self.parser(self.Arguments.excludes)
        self.distinct = self.get_distinct()
        self.qdistinct = self.get_qdistinct()
        self.fdistinct = self.get_fdistinct()
        self.limit = self.get_limits()
        self.order = self.get_order()

    def get_distinct(self):
        param = self.args.get(self.Arguments.distinct) if self.request else None
        logger.info("distinct: %s" % param, self.request.user if self.request else None, app=self.__class__.__name__)
        return True if param else False

    def get_qdistinct(self):
        param = self.args.get(self.Arguments.qdistinct) if self.request else None
        logger.info("qdistinct: %s" % param, self.request.user if self.request else None, app=self.__class__.__name__)
        return param.split(self.Separators._category) if test(param) else self.qdistinct

    def get_fdistinct(self):
        param = self.args.get(self.Arguments.fdistinct) if self.request else None
        logger.info("fdistinct: %s" % param, self.request.user if self.request else None, app=self.__class__.__name__)
        return param.split(self.Separators._category) if test(param) else self.fdistinct

    def get_limits(self):
        param = self.args.get(self.Arguments.limit) if self.request else None
        logger.info("limit: %s" % param, self.request.user if self.request else None, app=self.__class__.__name__)
        return param.split(self.Separators._pos) if test(param) else self.limit

    def get_order(self):
        param = self.args.get(self.Arguments.order) if self.request else None
        logger.info("order: %s" % param, self.request.user if self.request else None, app=self.__class__.__name__)
        return param.split(self.Separators._pos) if test(param) else self.order

    def dispatch(self, data):
        cat, fields = data.split(self.Separators._category)
        fs = [field.split(self.Separators._key) for field in fields.split(self.Separators._multiseparator)]
        sep = operator.and_
        if self.Separators._operator in cat:
            cat, sep = cat.split(self.Separators._operator)
            sep = operator.or_ if sep == "or" else operator.and_
        return sep, cat, fs

    def add_param(self, param, field, *args, **kwargs):
        mask = kwargs["mask"] if "mask" in kwargs else "icontains"
        logger.info("param: %s, field: %s, mask: %s" % (param, field, mask), self.request.user if self.request else None, app=self.__class__.__name__)
        if param not in self.nparams: self.nparams[param] = {"mask": mask, "fields": []}
        if field not in self.nparams[param]["fields"]: self.nparams[param]["fields"].append(field)

    def getQ(self, field, value, negative=False):
        if isinstance(value, str):
            if value[:1] == self.Separators._safe:
                return ~Q(**{field: value[1:]}) if negative else Q(**{field: value[1:]})    
            return ~Q(**{field: make_searchable(value)}) if negative else Q(**{field: make_searchable(value)})
        return ~Q(**{field: value}) if negative else Q(**{field: value})

    def getQ_range(self, field, value, op):
        values = value.split(self.Separators._range)
        return self.getQ("%s__gte" % field, values[0]) & self.getQ("%s__lte" % field, values[1])

    def getQ_in(self, field, value, op):
        values = value.split(self.Separators._in)
        return self.getQ("%s__in" % field, values)

    def getQ_list(self, field, value, op):
        values = value.split(self.Separators._list)
        if op == Q.OR: return reduce(operator.or_, (self.getQ(field, value) for  value in values))
        return reduce(operator.and_, (self.getQ(field, value) for  value in values))

    def getQ_bool(self, field, value, op):
        value = True if value.lower() == "true" else False
        return self.getQ(field, value)

    def field(self, field, value):
        if self.Separators._marker in field:
            field = field.split(self.Separators._marker)
            field[1] = field[1].split(self.Separators._operator)
            operator = Q.OR if len(field[1]) > 1 and field[1][1].lower() == "or" else Q.AND
            field[1] = field[1][0]
            if field[1] in self.Operators.authorized:
                return getattr(self, "getQ_%s" % field[1])(field[0], value, operator)
        else:
            return self.getQ(field, value)

    def parser(self, param):
        datas = self.args.get(param) if self.request else None
        parser = {}
        if test(datas):
            for data in datas.split(self.Separators._separator):
                fields_separator, category, fields = self.dispatch(data)
                if category not in parser: parser[category] = {"fields": [], "operator": operator.or_}
                qfields = [fields_separator]
                for field in fields: qfields.append(self.field(field[0], field[1]))
                parser[category]["fields"].append(qfields)
            logger.info("%s - array: %s" % (param, parser), self.request.user if self.request else None, app=self.__class__.__name__)
            sql = []
            for category, options in parser.items():
                sql.append(reduce(options["operator"], [reduce(fields.pop(0), (field for field in fields)) for fields in options["fields"]]))
            logger.info("%s - sql: %s" % (param, sql), self.request.user if self.request else None, app=self.__class__.__name__)
            return [parser, sql]
        return []

    def params(self):
        Qparams = Q()
        for param, options in self.nparams.items():
            datas = self.args.get(param) if self.request else None
            if test(datas):
                datas = datas.split(self.Separators._separator)                    
                Qparam = reduce(operator.or_, (self.getQ("%s__%s" % (field, options["mask"]), datas[0]) for field in options["fields"]))
                if len(datas) > 1:
                    for data in datas[1:]:
                        Qparam.add(reduce(operator.or_, (self.getQ("%s__%s" % (field, options["mask"]), data) for field in options["fields"])), Q.AND)
                Qparams.add(Qparam, Q.AND)
        return Qparams

    def get(self):
        queryset = self.get_queryset()
        if self.nparams:
            params = self.params()
            queryset = queryset.filter(params)
        if len(self.excludes):
            for sql in self.excludes[1]:
                queryset = queryset.exclude(sql)
        if len(self.filters):
            for sql in self.filters[1]:
                queryset = queryset.filter(sql)
        if self.qdistinct:
            queryset = queryset.filter(id__in=queryset.order_by(*self.qdistinct).distinct(*self.qdistinct).values("id"))
        if self.fdistinct:
            queryset = queryset.order_by(*self.fdistinct).distinct(*self.fdistinct)
        if self.distinct:
            queryset = queryset.distinct()
        if self.order:
            queryset = queryset.order_by(*self.order)
        if self.limit:
            queryset = queryset[int(self.limit[0]):int(self.limit[1])]
        return queryset