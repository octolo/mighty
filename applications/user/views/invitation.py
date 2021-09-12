from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from mighty.models import Invitation
from mighty.applications.user import fields
from mighty.views import DetailView
from mighty.applications.user.choices import STATUS_PENDING

class InvitationBaseView:
    model = Invitation
    queryset = Invitation.objects.all()
    slug_field = 'uid'
    slug_url_kwarg = 'uid'

    def get_object(self, queryset=None):
        args = {
            "uid": self.kwargs.get('uid', None), 
            "status": STATUS_PENDING,
            "token": self.request.GET.get('token', None)}
        return get_object_or_404(Invitation, **args)

    def actions(self, **kwargs):
        invitation = self.get_object()
        action = self.kwargs.get('action')
        if invitation.is_expired:
            action = 'expired'
            invitation.save()
        elif action == 'accepted':
            invitation.accepted(user=self.request.user if self.request.user.is_authenticated else None)
            invitation.save()
        elif action == 'refused':
            invitation.refused()
            invitation.save()
        return {field: str(getattr(invitation, field)) for field in fields.invitation[1:]}

class InvitationDetailView(InvitationBaseView, DetailView):
    model = Invitation
    queryset = Invitation.objects.all()

    def get_context_data(self, **kwargs):
        invitation = self.actions()
        return self.actions()

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, **response_kwargs)

if 'rest_framework' in settings.INSTALLED_APPS:
    from rest_framework.generics import RetrieveAPIView
    from rest_framework.response import Response
    
    class InvitationDetail(InvitationBaseView, RetrieveAPIView):
        permission_classes = ()

        def get(self, request, uid, action=None, format=None):
            return Response(self.actions())
