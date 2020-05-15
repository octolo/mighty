from django.conf import settings
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect

from mighty.views.viewsets import ModelViewSet
from mighty.views import DetailView, FormView, BaseView
from mighty.functions import decrypt
from mighty.applications.user.forms import UserCreationForm

from mighty.models.applications.twofactor import Twofactor
from mighty.applications.twofactor.forms import UserSearchForm, TwoFactorForm, SignUpForm
from mighty.applications.twofactor.apps import TwofactorConfig
from mighty.applications.twofactor import translates as _

from django.urls import reverse, NoReverseMatch
from urllib.parse import quote_plus, unquote_plus, urlencode
from mighty.functions import encrypt

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

    def set_url_by_method(self, user, method):
        try:
            useruidandmethod = '%s:%s' % (method, str(user.uid))
            useruidandmethod = encrypt(settings.SECRET_KEY[:16], useruidandmethod).decode('utf-8')
            self.success_url = reverse('mighty:twofactor-%s' % method, kwargs={'uid': quote_plus(useruidandmethod)})
        except NoReverseMatch:
            raise forms.add_error(None,'test error reverse')

    def form_valid(self, form):
        self.set_url_by_method(form.user_cache, form.method_cache)
        if self.request.GET: self.success_url += "?%s" % urlencode(self.request.GET, quote_via=quote_plus)
        return super().form_valid(form)

class Register(Login):
    form_class = SignUpForm
    over_add_to_context = { 'register': _.register, 'submit': _.submit_register, "help": _.help_register }

    def form_valid(self, form):
        from mighty.applications.twofactor import send_sms, send_email, translates as _
        user = form.save()
        if user.phone:
            status = send_sms(user)
            self.set_url_by_method(user, 'sms')
            self.success_url += "?phone=%s" % user.phone
        else:
            status = send_email(user)
            self.set_url_by_method(user, 'email')
            self.success_url += "?email=%s" % user.email
        return super(FormView, self).form_valid(form)

class LoginView(BaseView, LoginView):
    redirect_authenticated_user=True
    over_no_permission = True
    app_label = 'mighty'
    model_name = 'twofactor'
    form_class = TwoFactorForm
    over_add_to_context = {"help": _.help_login,}

    def get_form_kwargs(self):
        kwargs = super(LoginView, self).get_form_kwargs()
        useruidandmethod = decrypt(settings.SECRET_KEY[:16], unquote_plus(self.kwargs.get('uid'))).decode('utf-8').split(':')
        kwargs.update({'request' : self.request, 'uid': useruidandmethod[1], 'method': useruidandmethod[0]})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'message_email': _.message_email % self.request.GET.get('email') if self.request.GET.get('email') else None,
            'message_phone': _.message_phone % self.request.GET.get('phone') if self.request.GET.get('phone') else None
        })
        return context

class LoginEmail(LoginView):
    over_add_to_context = {'howto': _.howto_email_code, 'submit': _.submit_code, "help": _.help_email}

class LoginSms(LoginView):
    over_add_to_context = {'howto': _.howto_sms_code, 'submit': _.submit_code, "help": _.help_sms}

class LoginBasic(LoginView):
    over_add_to_context = {'howto': _.howto_basic_code, 'submit': _.submit_code, "help": _.help_basic}

class Logout(BaseView, LogoutView):
    over_no_permission = True
    app_label = 'mighty'
    model_name = 'twofactor'
    over_add_to_context = {'howto': _.howto_logout, 'title': _.logout}

class TwofactorViewSet(ModelViewSet):
    model = Twofactor
    slug = '<str:uid>'

    def __init__(self):
        super().__init__()
        self.add_view('register', Register, 'register/')
        self.add_view('login', Login, 'login/')
        self.add_view('email', LoginEmail, 'login/email/%s/' % self.slug)
        self.add_view('sms', LoginSms, 'login/sms/%s/' % self.slug)
        self.add_view('basic', LoginBasic, 'login/basic/%s/' % self.slug)
        self.add_view('logout', Logout, 'logout/')
