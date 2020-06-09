from django.conf import settings
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.urls import reverse, NoReverseMatch

from mighty.views.viewsets import ModelViewSet
from mighty.views import DetailView, FormView, BaseView
from mighty.models import Twofactor
from mighty.applications.user.forms import UserCreationForm
from mighty.applications.twofactor.forms import UserSearchForm, TwoFactorForm, SignUpForm
from mighty.applications.twofactor.apps import TwofactorConfig
from mighty.applications.twofactor import translates as _, send_sms, send_email
from urllib.parse import quote_plus, unquote_plus, urlencode


class LoginStepOne(FormView):
    redirect_authenticated_user = True
    over_no_permission = True
    form_class = UserSearchForm
    template_name = 'twofactor/stepone.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        return super().get(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': _.login,
            "help": _.help_login,
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

    def set_session_with_uid(self, uid):
        self.request.session['login_uid'] = uid

    def form_valid(self, form):
        self.set_session_with_uid(str(form.user_cache.uid))
        self.success_url = reverse('mighty:twofactor-second')
        return super().form_valid(form)

class Register(LoginStepOne):
    form_class = SignUpForm
    over_add_to_context = { 'register': _.register, 'submit': _.submit_register, "help": _.help_register }

    def form_valid(self, form):
        user = form.save()
        if 'groups_onsave' in settings.TWOFACTOR:
            for group in settings.TWOFACTOR['groups_onsave']:
                group = Group.objects.get(name=group) 
                user.groups.add(group)
        self.set_session_with_uid(str(user.uid))
        if user.phone:
            status = send_sms(user)
            self.set_url_by_method('sms')
            self.success_url += "?sms=%s" % user.phone
        else:
            status = send_email(user)
            self.set_url_by_method(user, 'email')
            self.success_url += "?email=%s" % user.email
        return super(FormView, self).form_valid(form)

class LoginStepTwo(BaseView, LoginView):
    redirect_authenticated_user = True
    over_no_permission = True
    form_class = TwoFactorForm
    template_name = 'twofactor/steptwo.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request' : self.request, 'uid': self.request.session['login_uid']})
        return kwargs

    def form_valid(self, form):
        del self.request.session['login_uid']
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'submit': _.submit_code, 'howto': _.howto_basic_code, 'help': _.help_basic })
        if self.request.GET.get('email'):
            context.update({
                'howto': _.howto_email_code,
                'message': _.message_email % self.request.GET.get('email'),
                'help': _.help_email,
            })
        elif self.request.GET.get('sms'):
            context.update({
                'howto': _.howto_sms_code,
                'message': _.message_sms % self.request.GET.get('sms'),
                'help': _.help_sms,
            })
        return context

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
        self.add_view('login', LoginStepOne, 'login/')
        self.add_view('second', LoginStepTwo, 'login/second/')
        self.add_view('logout', Logout, 'logout/')
