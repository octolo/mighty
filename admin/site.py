from django.contrib import admin
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import LoginView
from django.urls import reverse, resolve
from django.views.decorators.cache import never_cache

from mighty import translates as _
from mighty.apps import MightyConfig

class AdminSite(admin.AdminSite):
    site_header = MightyConfig.site_header
    index_title = MightyConfig.index_title

    @never_cache
    def login(self, request, extra_context=None):
        current_url = resolve(request.path_info).url_name

        if request.method == 'GET' and self.has_permission(request):
            index_path = reverse('admin:index', current_app=self.name)
            return HttpResponseRedirect(index_path)

        context = dict(
            self.each_context(request),
            title=_.login,
            app_path=request.get_full_path(),
            username=request.user.get_username(),
            current_url=current_url,
            next_url=request.GET.get('next', '')
        )
        if (REDIRECT_FIELD_NAME not in request.GET and REDIRECT_FIELD_NAME not in request.POST):
            context[REDIRECT_FIELD_NAME] = reverse('admin:index', current_app=self.name)
        context.update(extra_context or {})

        defaults = {
            'extra_context': context,
            'authentication_form': AdminAuthenticationForm,
            'template_name': self.login_template or 'admin/login.html',
        }
        request.current_app = self.name
        return LoginView.as_view(**defaults)(request)