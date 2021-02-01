from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.validators import  ValidationError
from django.db.models import Q

from mighty import filters
from mighty.views import DetailView, ListView, CheckData
from mighty.applications.user.choices import STATUS_PENDING
from mighty.applications.tenant.apps import TenantConfig
from mighty.applications.tenant import get_tenant_model, filters as tenant_filters, fields as tenant_fields
from itertools import chain

Role = get_tenant_model(TenantConfig.ForeignKey.role)
Invitation = get_tenant_model(TenantConfig.ForeignKey.invitation)
TenantModel = get_tenant_model(TenantConfig.ForeignKey.tenant)
TenantAlternate = get_tenant_model(TenantConfig.ForeignKey.alternate)
TenantGroup = get_tenant_model(TenantConfig.ForeignKey.group)

"""
Base
"""

class RoleBase:
    filters = [
        filters.SearchFilter(),
        tenant_filters.SearchByGroupUid(),
        tenant_filters.SearchByRoleUid(field='uid')
    ]

    def get_queryset(self, queryset=None):
        group = Q(group__in=self.request.user.user_tenant.all().values_list('group', flat=True))
        self.queryset = Role.objectsB.filter(group)
        return super().get_queryset(queryset)

    def get_fields(self, role):
        return {field: str(getattr(role, field)) for field in ('uid',) + tenant_fields.role}

class TenantBase:
    model = TenantModel
    queryset = TenantModel.objectsB.all()
    slug_field = 'uid'
    slug_url_kwarg = 'uid'

    def get_object(self):
        args = {
            "user": self.request.user,
            "uid": self.kwargs.get('uid', None),
        }
        return get_object_or_404(self.model, **args)

    def get_queryset(self, queryset=None):
        return self.queryset.filter(user=self.request.user)

    def get_fields(self, tenant):
        return {
            "uid": tenant.uid,
            "status": tenant.status,
            "company_representative": tenant.company_representative,
            "sync": tenant.sync,
            "group": {
                "uid": str(tenant.group.uid),
                "denomination": str(tenant.group.denomination),
                "image_url": str(tenant.group.image_url)
            },
            "roles": [{'uid': role.uid, 'name': role.name} for role in tenant.roles.all()]
        }

    def get_tenants(self):
        return [self.get_fields(tenant) for tenant in self.get_queryset()]

class InvitationBase:
    model = Invitation
    queryset = Invitation.objects.all()
    slug_field = 'uid'
    slug_url_kwarg = 'uid'

    def get_queryset(self, queryset=None):
        return self.queryset.filter(email__in=self.request.user.get_emails())

    def get_object(self, queryset=None):
        args = { 
            "uid": self.kwargs.get('uid', None), 
            "status": STATUS_PENDING }
        token = self.request.GET.get('token')
        if token: args['token'] = token
        else: args["email__in"] = self.request.user.get_emails()
        return get_object_or_404(self.model, **args)

    def get_fields(self, invitation):
        return {field: str(getattr(invitation, field)) for field in ('uid',) + tenant_fields.tenant_invitation}

    def actions(self):
        invitation = self.get_object()
        if invitation.status == STATUS_PENDING:
            action = self.kwargs.get('action')
            if invitation.is_expired:
                invitation.expired()
            elif action == 'accepted':
                invitation.accepted(user=self.request.user if self.request.user.is_authenticated else None)
            elif action == 'refused':
                invitation.refused()
            return invitation

"""
Django Views
"""

@method_decorator(login_required, name='dispatch')
class RoleList(RoleBase, ListView):
    def get_context_data(self, **kwargs):
        return [self.get_fields(role) for role in self.get_queryset()]

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, safe=False, **response_kwargs)

@method_decorator(login_required, name='dispatch')
class RoleCheckData(CheckData):
    test_field = "name__iexact"
    model = Role

    def get_queryset(self, queryset=None):
        try:
            group = TenantGroup.objects.get(uid=self.request.GET.get('group'))
            self.model.objects.get(**{self.test_field: self.request.GET.get('exist'), "group": group})
        except TenantGroup.DoesNotExist:
            assert ValidationError('group mandatory')

@method_decorator(login_required, name='dispatch')
class TenantList(TenantBase, ListView):
    def get_context_data(self, **kwargs):
        return self.get_tenants()

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, safe=False, **response_kwargs)

@method_decorator(login_required, name='dispatch')
class TenantDetail(TenantBase, DetailView):
    def get_context_data(self, **kwargs):
        return self.get_fields(self.get_object())

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, safe=False, **response_kwargs)

@method_decorator(login_required, name='dispatch')
class CurrentTenant(TenantBase, DetailView):
    def get_context_data(self, **kwargs):
        tenant = self.get_object()
        if tenant:
            self.request.user.tenant = tenant
            self.request.user.save()
        return self.get_fields(tenant)

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, safe=False, **response_kwargs)

@method_decorator(login_required, name='dispatch')
class InvitationList(InvitationBase, ListView):
    def get_context_data(self, **kwargs):
        return [self.get_fields(invitation) for invitation in self.get_queryset()]

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, safe=False, **response_kwargs)

@method_decorator(login_required, name='dispatch')
class InvitationDetail(InvitationBase, DetailView):
    def get_context_data(self, **kwargs):
        invitation = self.actions()
        return self.get_fields(invitation)

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, **response_kwargs)

"""
DRF Views
"""

if 'rest_framework' in settings.INSTALLED_APPS:
    from rest_framework.generics import RetrieveAPIView, ListAPIView, RetrieveAPIView
    from rest_framework.response import Response
    from mighty.applications.tenant.serializers import RoleSerializer, TenantSerializer

    class RoleList(RoleBase, ListAPIView):
        def get(self, request, format=None):
            return [self.get_fields(role) for role in self.get_queryset()]

    class TenantList(TenantBase, ListAPIView):
        def get(self, request, format=None):
            return Response(self.get_tenants())

    class TenantDetail(TenantBase, RetrieveAPIView):
        def get(self, request, uid, action=None, format=None):
            tenant = self.get_object()
            return Response(self.get_fields(tenant))

    class CurrentTenant(TenantBase, RetrieveAPIView):
        serializer_class = TenantSerializer

        def get(self, request, uid, action=None, format=None):
            tenant = self.get_object()
            self.request.user.current_tenant = tenant
            self.request.user.save()
            return Response(self.get_fields(tenant))

    class InvitationList(InvitationBase, ListAPIView):
        def get(self, request, format=None):
            return [self.get_fields(invitation) for invitation in self.get_queryset()]

    class InvitationDetail(InvitationBase, RetrieveAPIView):
        def get(self, request, uid, action=None, format=None):
            invitation = self.actions()
            return Response(self.get_fields(invitation))
