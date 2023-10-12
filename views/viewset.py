from django.db.models import Q
from django.http import Http404, HttpResponse

from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from mighty.filters import Foxid, FiltersManager
from mighty.forms.descriptors import FormDescriptor
from mighty.tables.descriptors import TableDescriptor

class ModelViewSet(ModelViewSet):
    cache_manager = None
    filters = []
    user_way = "user__id"
    action_prefix = "action_"
    order_enable = False
    order_base = []
    forms_desc = []
    tables_desc = []
    file_type = ("csv", "xls", "xlsx", "pdf")
    actions_authorized = ()
    variables_related = {}
    variables_model = []

    @property
    def model_static(self):
        return self.serializer_class.Meta.model

    @action(detail=False, methods=["get"])
    def reporting_list(self, request, *args, **kwargs):
        return Response(self.model_static().reporting_definition)

    @action(detail=True, methods=["get"])
    def reporting_detail(self, request, *args, **kwargs):
        obj = self.get_object()
        return obj.reporting_execute(request, *args, **kwargs)
        #report = request.GET.get("report")
        #filetype = request.GET.get("file")
        #if any(report, filetype) and filetype in self.file_type and report in obj.reporting_keys:
        #    return obj.reporting_process(reporting, file_type)
        #raise Http404()

    @action(detail=False, methods=["get"])
    def reporting(self, request, *args, **kwargs):
        obj = self.model_static()
        report = request.GET.get("report")
        filetype = request.GET.get("file")
        if any(report, filetype) and filetype in self.file_type and report in obj.reporting_keys:
            return obj.reporting_process(reporting, file_type)
        raise Http404()


    @action(detail=False, methods=["get"], url_path=r"forms/(?P<form>\w+)")
    def form_desc(self, request, form=None, *args, **kwargs):
        desc = next((f for f in self.forms_desc if f.Options.url == form), None)
        if desc:
            formdesc = FormDescriptor(desc, self.request, drf_kwargs=self.kwargs, **kwargs).as_json()
            return Response(formdesc)
        raise Http404

    @action(detail=True, methods=["get"], url_path=r"formsdetail/(?P<form>\w+)")
    def form_detail_desc(self, request, form=None, *args, **kwargs):
        desc = next((f for f in self.forms_desc if f.Options.url == form), None)
        if desc:
            formdesc = FormDescriptor(desc, self.request, drf_kwargs=self.kwargs, obj=self.get_object(), **kwargs).as_json()
            return Response(formdesc)
        raise Http404

    def call_action_model(self, obj, action, data, method):
        return

    @action(detail=True, methods=['get', 'post', 'delete'], url_path=r"saction/(?P<saction>\w+)")
    def single_action(self, *args, **kwargs):
        saction = kwargs.get("saction")
        if saction in self.actions_authorized:
            obj = self.get_object()
            if hasattr(obj, saction):
                result = getattr(obj, saction)()
                return Response(result)
        raise Http404

    @action(detail=True, methods=['get', 'post', 'delete'], url_path=r"daction/(?P<daction>\w+)")
    def data_action(self, *args, **kwargs):
        daction = kwargs.get("daction")
        action = self.action_prefix+daction
        if action in self.actions_authorized:
            obj = self.get_object()
            if hasattr(obj, daction):
                result = getattr(obj, daction)(self.request.data, self.request.method)
                return Response(result)
        raise Http404

    @action(detail=False, methods=["get"], url_path=r"table/(?P<table>\w+)")
    def table_desc(self, request, table=None, *args, **kwargs):
        desc = next((f for t in self.tables_desc if t.Options.url == table), None)
        if desc:
            formdesc = TableDescriptor(desc, request, **kwargs).as_json()
            return Response(formdesc)
        raise Http404

    @action(detail=False, methods=["get"])
    def variables(self, request, *args, **kwargs):
        model = self.model_static
        if hasattr(self.model_static, 'eve_variable_prefixed_list'):
            var = self.model_static().eve_variable_prefixed_list(related=self.variables_related)
            #var += list(itertools.chain(*(v().eve_variable_prefixed_list() for v in self.variables_model)))
            return Response(var)
        return Response([])

    # Variables access
    @action(detail=True, methods=["get"])
    def variablesviewer(self, request, *args, **kwargs):
        obj = self.get_object()
        variable = obj.eve_tv.get(request.GET.get("eve_tv"))
        return HttpResponse(variable)

    # Filter query
    def Q_is_me(self, prefix=""):
        return Q(**{prefix+self.user_way: self.user.id})

    # Queryset
    def get_queryset(self, queryset=None):
        return self.foxid.filter(*self.manager.params(self.request))

    @property
    def foxid(self):
        return Foxid(self.queryset, self.request, f=self.manager.flts, order_base=self.order_base, order_enable=self.order_enable).ready()

    def foxid_qs(self, qs, flts, order_base=None):
        return Foxid(qs, self.request, f=flts, order_base=order_base or self.order_base).ready()

    @property
    def manager(self):
        if not self.cache_manager:
            self.cache_manager = FiltersManager(flts=self.filters)
        return self.cache_manager

    def manager_flts(self, flts):
        return FiltersManager(flts=flts)

    # Properties
    @property
    def user(self):
        return self.request.user

    @property
    def user_groups(self):
        return self.user.groups.all()

    @property
    def user_groups_pk(self):
        return [group.pk for group in self.user_groups]

    @property
    def is_staff(self):
        return self.user.is_staff

    @property
    def is_superuser(self):
        return self.user.is_superuser

    # Actions
    @action(detail=True, methods=['get'])
    def enable(self, request, pk=None):
        instance = self.get_object()
        instance.enable()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def disable(self, request, pk=None):
        instance = self.get_object()
        instance.disable()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
