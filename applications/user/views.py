from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.validators import EmailValidator, ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from mighty.models import Invitation
from mighty.applications.user.forms import UserCreationForm
from mighty.applications.user.apps import UserConfig
from mighty.applications.user import fields
from mighty.views import TemplateView, DetailView, AddView, CheckData
from mighty.applications.user.choices import STATUS_PENDING
from mighty.applications.user.forms import UserCreationForm
from mighty.models import UserEmail, UserPhone
from mighty.functions import make_searchable

from phonenumber_field.validators import validate_international_phonenumber

"""
Base Views
"""
UserModel = get_user_model()
class ProfileBase:
    model = UserModel

    def get_object(self, queryset=None):
        user = self.request.user
        newstyle = self.request.GET.get('use', UserConfig.Field.style[0])
        if newstyle != user.style:
            user.style = newstyle
            user.save()
        newlang = self.request.GET.get('lang')
        if newlang != user.language_pref:
            try:
                from mighty.models import Nationality
                newlang = Nationality.objects.get(alpha2__icontains=newlang)
                user.language = newlang
                user.save()
            except Exception:
                pass
        return user

    def get_fields(self):
        user = self.get_object()
        user_data = {'uid': str(user.uid)}
        user_data.update({field: getattr(user, field) for field in fields.profile})
        if hasattr(user, 'current_tenant') and user.current_tenant:
            user_data.update({'current_tenant': user.current_tenant.uid})
        return user_data

class InvitationBase:
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

"""
Django Views
"""
@method_decorator(login_required, name='dispatch')
class Profile(ProfileBase, DetailView):
    def get_context_data(self, **kwargs):
        return self.get_fields()

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, **response_kwargs)

class InvitationDetail(InvitationBase, DetailView):
    model = Invitation
    queryset = Invitation.objects.all()

    def get_context_data(self, **kwargs):
        invitation = self.actions()
        return self.actions()

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, **response_kwargs)

class CreateUser(AddView):
    form_class = UserCreationForm
    template_name = 'mighty/form.html'
    model = UserModel
    
    def get_success_url(self):
        return reverse('generic-success')

class UserEmailCheck(CheckData):
    permission_classes = ()
    model = UserEmail
    test_field = 'email'

    def get_data(self):
        return make_searchable(self.request.GET.get('check').lower())

    def check_data(self):
        validator = EmailValidator()
        try:
            validator(self.get_data())
            return super().check_data()
        except ValidationError as e:
            return { "code": "002", "error": str(e.message) }

class UserPhoneCheck(CheckData):
    permission_classes = ()
    model = UserPhone
    test_field = 'phone'

    def check_data(self):
        try:
            phone = "+" + self.request.GET.get('check')
            validate_international_phonenumber(phone)
            return super().check_data()
        except ValidationError as e:
            return { "code": "002", "error": str(e.message) }    

"""
DRF Views
"""
if 'rest_framework' in settings.INSTALLED_APPS:
    from rest_framework.generics import RetrieveAPIView, CreateAPIView
    from rest_framework.response import Response
    from mighty.applications.user.serializers import UserSerializer, CreateUserSerializer
    from rest_framework.renderers import JSONRenderer
    from rest_framework.decorators import renderer_classes
    
    class Profile(ProfileBase, RetrieveAPIView):
        def get(self, request, format=None):
            return Response(self.get_fields())

    class InvitationDetail(InvitationBase, RetrieveAPIView):
        permission_classes = ()

        def get(self, request, uid, action=None, format=None):
            return Response(self.actions())

    class CreateUser(CreateAPIView):
        permission_classes = ()
        serializer_class = CreateUserSerializer
        model = UserModel