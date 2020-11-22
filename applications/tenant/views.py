from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from mighty.views import DetailView, ListView
from mighty.applications.user.choices import STATUS_PENDING
from mighty.applications.tenant import get_tenant_model
from itertools import chain

Invitation = get_tenant_model(settings.TENANT_INVITATION)


@method_decorator(login_required, name='dispatch')
class TenantList(ListView):
    def get_queryset(self, queryset=None):
        qs1 = get_tenant_model(settings.TENANT_MODEL).objectsB.filter(user=self.request.user)
        qs2 = get_tenant_model(settings.TENANT_ALTERNATE).objectsB.filter(user=self.request.user)
        return list(chain(qs1, qs2))
        
    def get_context_data(self, **kwargs):
        return [
        {
            "uid": tenant.uid,
            "status": tenant.status,
            "company_representative": tenant.company_representative,
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