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


from django.shortcuts import redirect
class Login(FormView):
    redirect_authenticated_user=True
    over_no_permission = True
    app_label = 'mighty'
    model_name = 'twofactor'
    form_class = UserSearchForm

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        return super().get(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': _.login,
            'meta': {'title': _.login},
            'enable_email': TwofactorConfig.method.email,
            'enable_sms': TwofactorConfig.method.sms,
            'enable_basic': TwofactorConfig.method.basic,
            'send_method': _.send_method,
            'send_basic': _.send_basic,
            'method_email': _.method_email,
            'method_sms': _.method_sms,
            'method_basic': _.method_basic,
        })
        return context

    def form_valid(self, form):
        self.user = form.user_cache
        self.method = form.method_cache
        from urllib.parse import urlencode, quote_plus
        self.success_url = form.success_url
        if self.request.GET: self.success_url += "?%s" % urlencode(self.request.GET, quote_via=quote_plus)
        return super().form_valid(form)

class LoginView(BaseView, LoginView):
    redirect_authenticated_user=True
    over_no_permission = True
    app_label = 'mighty'
    model_name = 'twofactor'
    form_class = TwoFactorForm

    def get_form_kwargs(self):
        kwargs = super(LoginView, self).get_form_kwargs()
        useruidandmethod = decrypt(settings.SECRET_KEY[:16], unquote_plus(self.kwargs.get('uid'))).decode('utf-8').split(':')
        kwargs.update({'request' : self.request, 'uid': useruidandmethod[1], 'method': useruidandmethod[0]})
        return kwargs

class LoginEmail(LoginView):
    over_add_to_context = {'howto': _.howto_email_code, 'submit': _.submit_code}

class LoginSms(LoginView):
    over_add_to_context = {'howto': _.howto_sms_code, 'submit': _.submit_code}

class LoginBasic(LoginView):
    over_add_to_context = {'howto': _.howto_basic_code, 'submit': _.submit_code}

class Logout(BaseView, LogoutView):
    app_label = 'mighty'
    model_name = 'twofactor'
    over_add_to_context = {'howto': _.howto_logout, 'title': _.logout}

class TwofactorViewSet(ModelViewSet):
    model = Twofactor
    slug = '<str:uid>'

    def __init__(self):
        super().__init__()
        self.add_view('login', Login, 'login/')
        self.add_view('email', LoginEmail, 'login/email/%s/' % self.slug)
        self.add_view('sms', LoginSms, 'login/sms/%s/' % self.slug)
        self.add_view('basic', LoginBasic, 'login/basic/%s/' % self.slug)
        self.add_view('logout', Logout, 'logout/')
