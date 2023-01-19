from django.db.models import Q
from django.http import Http404
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
    order_base = []
    forms_desc = []
    tables_desc = []


    @action(detail=False, methods=["get"], url_path=r"forms/(?P<form>\w+)")
    def form_desc(self, request, form=None, *args, **kwargs):
        desc = next((f for f in self.forms_desc if f.Options.url == form), None)
        if desc:
            formdesc = FormDescriptor(desc, self.request, drf_kwargs=self.kwargs, **kwargs).as_json()
            return Response(formdesc)
        raise Http404
        
    def call_action_model(self, obj, action, data, method):
        return getattr(obj, action)(data, method)

    @action(detail=True, methods=['get', 'post', 'delete'], url_path=r"action/(?P<action>\w+)")
    def actions(self, request, uid, action, *args, **kwargs):
        obj = self.get_object()
        action = self.action_prefix+action
        if hasattr(obj, action):
            infos = self.call_action_model(obj, action, self.request.data, self.request.method)
            return Response({"infos": infos})
        raise Http404

    @action(detail=False, methods=["get"], url_path=r"table/(?P<table>\w+)")
    def table_desc(self, request, table=None, *args, **kwargs):
        desc = next((f for t in self.tables_desc if t.Options.url == table), None)
        if desc:
            formdesc = TableDescriptor(desc, request, **kwargs).as_json()
            return Response(formdesc)
        raise Http404

    # Filter query
    def Q_is_me(self, prefix=""):
        return Q(**{prefix+self.user_way: self.user.id})

    # Queryset
    def get_queryset(self, queryset=None):
        return self.foxid.filter(*self.manager.params(self.request))

    @property
    def foxid(self):
        return Foxid(self.queryset, self.request, f=self.manager.flts, order_base=self.order_base).ready()

    def foxid_qs(self, qs, flts):
        return Foxid(qs, self.request, f=flts, order_base=self.order_base).ready()

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