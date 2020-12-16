from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.validators import  ValidationError
from django.db.models import Q

from mighty import filters
from mighty.views import DetailView, ListView, AlreadyExist
from mighty.applications.user.choices import STATUS_PENDING
from mighty.applications.tenant.apps import TenantConfig
from mighty.applications.tenant import get_tenant_model, filters as tenant_filters
from itertools import chain

Role = get_tenant_model(TenantConfig.ForeignKey.role)
Invitation = get_tenant_model(TenantConfig.ForeignKey.invitation)
TenantModel = get_tenant_model(TenantConfig.ForeignKey.tenant)
TenantAlternate = get_tenant_model(TenantConfig.ForeignKey.alternate)
TenantGroup = get_tenant_model(TenantConfig.ForeignKey.group)



@method_decorator(login_required, name='dispatch')
class RoleList(ListView):
    filters = [
        filters.SearchFilter(),
        tenant_filters.SearchByGroupUid(),
        tenant_filters.SearchByRoleUid(field='uid')
    ]

    def get_queryset(self, queryset=None):
        group = Q(group__in=self.request.user.user_tenant.all().values_list('group', flat=True))
        self.queryset = Role.objectsB.filter(group)
        return super().get_queryset(queryset)

    def get_context_data(self, **kwargs):
        return [{
            'uid': role.uid,
            'name': role.name,
            'is_immutable': role.is_immutable,
            'group': role.group.uid,
        } for role in self.get_queryset()]

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, safe=False, **response_kwargs)

@method_decorator(login_required, name='dispatch')
class RoleAlreadyExist(AlreadyExist):
    test_field = "name__iexact"
    model = Role

    def get_queryset(self, queryset=None):
        try:
            group = TenantGroup.objects.get(uid=self.request.GET.get('group'))
            self.model.objects.get(**{self.test_field: self.request.GET.get('exist'), "group": group})
        except TenantGroup.DoesNotExist:
            assert ValidationError('group mandatory')

@method_decorator(login_required, name='dispatch')
class TenantList(ListView):
    def get_queryset(self, queryset=None):
        print('tatatatata')
        qs1 = TenantModel.objectsB.filter(user=self.request.user)
        qs2 = TenantAlternate.objectsB.filter(user=self.request.user)
        return list(chain(qs1, qs2))
        
    def get_context_data(self, **kwargs):
        return [
        {
            "uid": tenant.uid,
            "status": tenant.status,
            "company_representative": tenant.company_representative,
            "sync": tenant.sync,
            "group": {
                "uid": str(tenant.group.uid),
                "denomination": str(tenant.group.denomination),
                "image_url": str(tenant.group.image_url)
            }
        } for tenant in self.get_queryset()]

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, safe=False, **response_kwargs)

@method_decorator(login_required, name='dispatch')
class InvitationList(ListView):
    def get_queryset(self, queryset=None):
        return Invitation.objects.filter(email__in=self.request.user.get_emails())

    def get_context_data(self, **kwargs):
        return [
        {
            "uid": invitation.uid,
            "group": str(invitation.group),
            "by": invitation.by.representation,
            "email": invitation.email,
            "status": invitation.status
        } for invitation in self.get_queryset()]

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, safe=False, **response_kwargs)

@method_decorator(login_required, name='dispatch')
class InvitationDetail(DetailView):
    model = Invitation
    queryset = Invitation.objects.all()
    slug_field = 'uid'
    slug_url_kwarg = 'uid'

    def get_object(self, queryset=None):
        args = { 
            "uid": self.kwargs.get('uid', None), 
            "status": STATUS_PENDING,
        }
        token = self.request.GET.get('token')
        if token:
            args['token'] = token
        else:
            args["email__in"] = self.request.user.get_emails()
        return get_object_or_404(Invitation, **args)

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

    def get_context_data(self, **kwargs):
        invitation = self.actions()
        return { 
            "uid": invitation.uid,
            "group": str(invitation.group),
            "tenant": invitation.tenant.uid if invitation.tenant else None,
            "by": invitation.by.representation,
            "email": invitation.email,
            "status": invitation.status
        }

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, **response_kwargs)


if 'rest_framework' in settings.INSTALLED_APPS:
    from rest_framework.generics import RetrieveAPIView, ListAPIView
    from rest_framework.response import Response

    class TenantList(ListAPIView):
        def get_queryset(self, queryset=None):
            qs1 = get_tenant_model(settings.TENANT_MODEL).objectsB.filter(user=self.request.user)
            qs2 = get_tenant_model(settings.TENANT_ALTERNATE).objectsB.filter(user=self.request.user)
            return list(chain(qs1, qs2))

        def get(self, request, format=None):
            return Response([
            {
                "uid": tenant.uid,
                "status": tenant.status,
                "company_representative": tenant.company_representative,
                "group": {
                    "uid": str(tenant.group.uid),
                    "denomination": str(tenant.group.denomination),
                    "image_url": str(tenant.group.image_url)
                }
            } for tenant in self.get_queryset()])

    class InvitationList(ListAPIView):
        def get_queryset(self, queryset=None):
            return Invitation.objects.filter(email__in=self.request.user.get_emails())
    
        def get(self, request, format=None):
            return Response([
            {
                "uid": invitation.uid,
                "group": str(invitation.group),
                "by": invitation.by.representation,
                "email": invitation.email,
                "status": invitation.status
            } for invitation in self.get_queryset()])

    class InvitationDetail(RetrieveAPIView):
        def get_object(self, queryset=None):
            args = { 
                "uid": self.kwargs.get('uid', None), 
            }
            token = self.request.GET.get('token')
            if token:
                args['token'] = token
            else:
                args["email__in"] = self.request.user.get_emails()
            return get_object_or_404(Invitation, **args)

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

        def get(self, request, uid, action=None, format=None):
            invitation = self.actions()
            return Response({
                "uid": invitation.uid,
                "group": str(invitation.group),
                "tenant": invitation.tenant.uid if invitation.tenant else None,
                "by": invitation.by.representation,
                "email": invitation.email,
                "status": invitation.status
            })