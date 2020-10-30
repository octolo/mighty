from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from mighty.models import Invitation
from mighty.applications.user.forms import UserCreationForm
from mighty.applications.user.apps import UserConfig
from mighty.views import DetailView, FormView, CreateView

UserModel = get_user_model()

class UserStyle(DetailView):
    model = UserModel

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        user = self.get_object()
        use = self.request.GET.get('use', UserConfig.Field.style[0])
        use = use if use in UserConfig.Field.style else UserConfig.Field.style[0]
        if use != self.request.user.style:
            self.request.user.style = use
            self.request.user.save()
        return { 'availables': UserConfig.Field.style, 'use': use }

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, **response_kwargs)

class UserMe(DetailView):
    model = UserModel

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        user = self.get_object()
        return {
            "uid": user.uid,
            "image_url": user.image_url,
            "username": user.username,
            "last_name": user.last_name,
            "first_name": user.first_name,
            "fullname": user.fullname,
            "representation": user.representation,
            "style": user.style,
            "get_gender_display": user.get_gender_display(),
            "is_staff": user.is_staff
        }

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, **response_kwargs)

class InvitationAction(DetailView):
    model = Invitation
    queryset = Invitation.objects.all()
    slug_field = 'uid'
    slug_url_kwarg = 'uid'

    def get_object(self, queryset=None):
        token = self.request.GET.get('token', None)
        uid = self.kwargs.get('uid', None)
        return get_object_or_404(Invitation, uid=uid, token=token)

    def get_context_data(self, **kwargs):
        invitation = self.get_object()
        action = self.kwargs.get('action')
        if invitation.is_expired:
            action = 'expired'
            invitation.save()
        elif action == 'accepted':
            invitation.accepted()
            invitation.save()
        elif action == 'refused':
            invitation.refused()
            invitation.save()
        return { "status": invitation.status, "action": action }

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, **response_kwargs)