from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from mighty.models import Invitation
from mighty.applications.user.forms import UserCreationForm
from mighty.applications.user.apps import UserConfig
from mighty.views import DetailView, FormView, CreateView
from mighty.applications.user.choices import STATUS_PENDING

UserModel = get_user_model()

@method_decorator(login_required, name='dispatch')
class UserMe(DetailView):
    model = UserModel

    def get_object(self, queryset=None):
        user = self.request.user
        newstyle = self.request.GET.get('use', UserConfig.Field.style[0])
        if newstyle != user.style:
            user.style = newstyle
            user.save()
        return user

    def get_context_data(self, **kwargs):
        user = self.get_object()
        return {
            "image_url": user.image_url,
            "username": user.username,
            "last_name": user.last_name,
            "first_name": user.first_name,
            "fullname": user.fullname,
            "representation": user.representation,
            "style": user.style,
            "get_gender_display": user.get_gender_display(),
            "is_staff": user.is_staff,
        }

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, **response_kwargs)

class InvitationDetail(DetailView):
    model = Invitation
    queryset = Invitation.objects.all()
    slug_field = 'uid'
    slug_url_kwarg = 'uid'

    def get_object(self, queryset=None):
        args = { 
            "uid": self.kwargs.get('uid', None), 
            "status": STATUS_PENDING,
            "token": self.request.GET.get('token', None)
        }
        return get_object_or_404(Invitation, **args)

    def actions(self):
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
        return invitation

    def get_context_data(self, **kwargs):
        invitation = self.actions()
        return { 
            "by": invitation.by.representation,
            "email": invitation.email,
            "status": invitation.status
        }

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, **response_kwargs)

if 'rest_framework' in settings.INSTALLED_APPS:
    from rest_framework.generics import RetrieveAPIView
    from rest_framework.response import Response
    from mighty.applications.user.serializers import UserSerializer

    class UserMe(RetrieveAPIView):
        def get_object(self, queryset=None):
            user = self.request.user
            newstyle = self.request.GET.get('use', UserConfig.Field.style[0])
            if newstyle != user.style:
                user.style = newstyle
                user.save()
            return user

        def get(self, request, format=None):
            user = self.get_object()
            return Response({
                "image_url": user.image_url,
                "username": user.username,
                "last_name": user.last_name,
                "first_name": user.first_name,
                "fullname": user.fullname,
                "representation": user.representation,
                "style": user.style,
                "get_gender_display": user.get_gender_display(),
                "is_staff": user.is_staff,
            })


    class InvitationDetail(RetrieveAPIView):
        permission_classes = ()

        def get_object(self, queryset=None):
            args = { 
                "uid": self.kwargs.get('uid', None), 
                "status": STATUS_PENDING,
                "token": self.request.GET.get('token', None)
            }
            return get_object_or_404(Invitation, **args)

        def actions(self):
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
            return invitation

        def get(self, request, uid, action=None, format=None):
            invitation = self.actions()
            return Response({
                "by": invitation.by.representation,
                "email": invitation.email,
                "status": invitation.status
            })