from django.conf import settings
from django.contrib.auth.views import LoginView, LogoutView

from mighty.views.viewsets import ModelViewSet
from mighty.views import DetailView, FormView, BaseView
from mighty.models.applications.twofactor import Twofactor

from mighty.functions import decrypt
from mighty.applications.twofactor.forms import UserSearchForm, TwoFactorForm
from mighty.applications.twofactor.apps import TwofactorConfig
from mighty.applications.twofactor import translates as _
from urllib.parse import quote_plus, unquote_plus

class Login(FormView):
    app_label = 'mighty'
    model_name = 'twofactor'
    form_class = UserSearchForm
    add_to_context = {
        'title': _.login,
        "meta": {'title': _.login},
        "enable_email": TwofactorConfig.method.email,
        "enable_sms": TwofactorConfig.method.sms,
        "enable_basic": TwofactorConfig.method.basic,
        "send_method": _.send_method,
        "send_basic": _.send_basic,
        'method_email': _.method_email,
        'method_sms': _.method_sms,
        'method_basic': _.method_basic,
    }

    def form_valid(self, form):
        self.user = form.user_cache
        self.method = form.method_cache
        self.success_url = form.success_url
        return super().form_valid(form)

class LoginView(BaseView, LoginView):
    app_label = 'mighty'
    model_name = 'twofactor'
    form_class = TwoFactorForm
    add_to_context = { "meta": {'title': _.login},}

    def get_form_kwargs(self):
        kwargs = super(LoginView, self).get_form_kwargs()
        useruidandmethod = decrypt(settings.SECRET_KEY[:16], unquote_plus(self.kwargs.get('uid'))).decode("utf-8").split(':')
        kwargs.update({'request' : self.request, 'uid': useruidandmethod[1], 'method': useruidandmethod[0]})
        return kwargs

class LoginEmail(LoginView):
    add_to_context = {"howto": _.howto_email_code, 'submit': _.submit_code, 'title': _.login, "meta": {'title': _.login},}

class LoginSms(LoginView):
    add_to_context = {"howto": _.howto_sms_code, 'submit': _.submit_code, 'title': _.login, "meta": {'title': _.login},}

class LoginBasic(LoginView):
    add_to_context = {"howto": _.howto_basic_code, 'submit': _.submit_code, 'title': _.login, "meta": {'title': _.login},}

class Logout(BaseView, LogoutView):
    app_label = 'mighty'
    model_name = 'twofactor'
    add_to_context = {"howto": _.howto_logout, 'title': _.logout, "meta": {'title': _.logout},}


class TwofactorViewSet(ModelViewSet):
    model = Twofactor