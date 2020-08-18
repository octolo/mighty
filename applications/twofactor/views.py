from django.conf import settings
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.urls import reverse, NoReverseMatch
from django.http import HttpResponseRedirect

from mighty.views import DetailView, FormView, BaseView
from mighty.models import Twofactor
from mighty.applications.user.forms import UserCreationForm
from mighty.applications.twofactor.forms import TwoFactorSearchForm, TwoFactorChoicesForm, TwoFactorCodeForm, SignUpForm
from mighty.applications.twofactor.apps import TwofactorConfig as conf
from mighty.applications.twofactor import translates as _
from mighty.applications.messenger import choices

from urllib.parse import quote_plus, unquote_plus, urlencode

class LoginStepSearch(LoginView):
    redirect_authenticated_user = True
    over_no_permission = True
    authentication_form = TwoFactorSearchForm
    template_name = 'twofactor/search.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        return super().get(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': _.login,
            'help': _.help_login,
            'enable_email': conf.method.email,
            'enable_sms': conf.method.sms,
            'enable_basic': conf.method.basic,
            'send_method': _.send_method,
            'send_basic': _.send_basic,
            'method_email': _.method_email,
            'method_sms': _.method_sms,
            'method_basic': _.method_basic,
            'mode_sms': choices.MODE_SMS,
            'mode_email': choices.MODE_EMAIL,
        })
        return context

    def get_success_url(self):
        return self.success_url or reverse('mighty:twofactor-choices')

    def form_valid(self, form):
        return HttpResponseRedirect(self.get_success_url())

class LoginStepChoices(BaseView, LoginStepSearch):
    redirect_authenticated_user = True
    over_no_permission = True
    form_class = TwoFactorChoicesForm
    template_name = 'twofactor/choices.html'

    def get_success_url(self):
        return self.success_url or reverse('mighty:twofactor-code')

    def form_valid(self, form):
        return HttpResponseRedirect(self.get_success_url())

class LoginStepCode(BaseView, LoginView):
    redirect_authenticated_user = True
    over_no_permission = True
    form_class = TwoFactorCodeForm
    template_name = 'twofactor/code.html'

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

    def get_success_url(self):
        return self.success_url or super().get_success_url()

class Logout(BaseView, LogoutView):
    over_no_permission = True
    app_label = 'mighty'
    model_name = 'twofactor'
    over_add_to_context = {'howto': _.howto_logout, 'title': _.logout}

class Register(LoginStepSearch):
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
            #status = send_sms(user)
            self.set_url_by_method('sms')
            self.success_url += "?sms=%s" % user.phone
        else:
            #status = send_email(user)
            self.set_url_by_method(user, 'email')
            self.success_url += "?email=%s" % user.email
        return super(FormView, self).form_valid(form)

#class TwofactorViewSet(ModelViewSet):
#    model = Twofactor
#    slug = '<str:uid>'
#
#    def __init__(self):
#        super().__init__()
#        self.add_view('register', Register, 'register/')
#        self.add_view('search', LoginStepSearch, 'login/')
#        self.add_view('choices', LoginStepChoices, 'login/choices/')
#        self.add_view('code', LoginStepCode, 'login/code/')
#        self.add_view('logout', Logout, 'logout/')
