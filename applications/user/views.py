from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from mighty.applications.user.forms import UserCreationForm
from mighty.applications.user.apps import UserConfig

from mighty.views import DetailView, FormView, CreateView
from mighty.views.viewsets import ModelViewSet
from mighty.models import User
from mighty.applications.user import translates as _, filters

is_ajax = True if 'rest_framework' in settings.INSTALLED_APPS else False

class UserRegister(FormView):
    model_name = 'user'
    app_label = 'auth'
    form_class = UserCreationForm
    fields = ('email', 'password')

class UserProfile(DetailView):
    model = User
    app_label = 'auth'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"meta": {"title": _.profil}})
        return context

class UserSwitchStyle(UserProfile):
    def get_context_data(self, **kwargs):
        style = self.kwargs['style'] if self.kwargs['style'] in UserConfig.Field.style else UserConfig.Field.style[0]
        self.request.user.style = style
        self.request.user.save()
        context = {'style': style }
        return context

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, **response_kwargs)

class UserViewSet(ModelViewSet):
    model = User
    is_ajax = is_ajax
    slug = '<uuid:uid>'
    slug_field = "uid"
    slug_url_kwarg = "uid"
    fields = ['username',]

    def __init__(self):
        super().__init__()
        self.add_view('profile', UserProfile, 'profile/')
        self.add_view('style', UserSwitchStyle, 'style/<str:style>/')

if 'rest_framework' in settings.INSTALLED_APPS:
    from mighty.views.viewsets import ApiModelViewSet
    from mighty.applications.user import serializers
    class UserApiViewSet(ApiModelViewSet):
        model = User
        slug = '<uuid:uid>'
        slug_field = "uid"
        slug_url_kwarg = "uid"
        lookup_field = "uid"
        serializer_class = serializers.UserSerializer
        filter_model = filters.UserFilter