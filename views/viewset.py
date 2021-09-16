from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from mighty.filters import Foxid, FiltersManager

class ModelViewSet(ModelViewSet):
    cache_manager = None
    filters = []
    user_way = "user__id"

    # Filter query
    def Q_is_me(self, prefix=""):
        return Q(**{prefix+self.user_way: self.user.id})

    # Queryset
    def get_queryset(self, queryset=None):
        return self.foxid.filter(*self.manager.params(self.request))

    @property
    def foxid(self):
        return Foxid(self.queryset, self.request, f=self.manager.flts).ready()

    @property
    def manager(self):
        if not self.cache_manager:
            self.cache_manager = FiltersManager(flts=self.filters)
        return self.cache_manager

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