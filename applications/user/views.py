from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from mighty.applications.user.forms import UserCreationForm
from mighty.applications.user.apps import UserConfig

from mighty.views import DetailView, FormView, CreateView
from mighty.models import User
from mighty.applications.user import translates as _

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

