from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect
from django.utils.text import capfirst
from django.urls import reverse, resolve
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.utils.translation import gettext

from mighty import translates as _
from mighty.apps import MightyConfig as conf
from mighty.functions import service_uptime, service_cpu, service_memory

from functools import update_wrapper

import logging
logger = logging.getLogger(__name__)

supervision = {
    'server': {
        'uptime': "cat /proc/uptime | awk '{ print $1}' | tr -d '\n'",
        'cpu': """cat /proc/loadavg | awk '{print $1"\\n"$2"\\n"$3}'""",
        'memory': "free | grep Mem | awk '{print $3/$2 * 100.0}' | tr -d ' '"
    }
}
supervision.update(getattr(settings, 'SUPERVISION', {}))

# async def channels_group(pattern):
#     redis = await aioredis.create_redis_pool(settings.CHANNEL_LAYERS['default']['CONFIG']['hosts'][0])
#     keys = await redis.keys(pattern, encoding='utf-8')
#     channels = {key.replace(pattern[:-1], ''): await redis.ttl(key) for key in keys}
#     redis.close()
#     await redis.wait_closed()
#     return channels

# async def flushdb():
#     redis = await aioredis.create_redis_pool(settings.CHANNEL_LAYERS['default']['CONFIG']['hosts'][0])
#     await redis.flushdb()
#     redis.close()
#     await redis.wait_closed()

class AdminSite(admin.AdminSite):
    enable_nav_sidebar = False
    site_header = conf.site_header
    index_title = conf.index_title

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        print("test", conf.urls_admin_to_add)
        extra_context['urls_admin_to_add'] = conf.urls_admin_to_add
        return super().index(request, extra_context=extra_context)

    def wrap(self, view):
        def wrapper(*args, **kwargs):
            return self.admin_view(view)(*args, **kwargs)
        wrapper.model_admin = self
        return update_wrapper(wrapper, view)

    def stepsearch(self, request, extra_context=None):
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
            next_url=request.GET.get('next', ''),
            is_nav_sidebar_enabled=False,
        )
        if (REDIRECT_FIELD_NAME not in request.GET and REDIRECT_FIELD_NAME not in request.POST):
            context[REDIRECT_FIELD_NAME] = reverse('admin:twofactor_choices', current_app=self.name)
        context.update(extra_context or {})

        from mighty.applications.twofactor.forms import TwoFactorSearchForm
        defaults = {
            'extra_context': context,
            'authentication_form': TwoFactorSearchForm,
            'success_url': reverse('admin:twofactor_choices'),
            'template_name': self.login_template or 'admin/search.html',
        }
        request.current_app = self.name
        from mighty.applications.twofactor.views import LoginStepSearch
        return LoginStepSearch.as_view(**defaults)(request)

    def stepchoices(self, request, extra_context=None):
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
            next_url=request.GET.get('next', ''),
            is_nav_sidebar_enabled=False,

        )
        if (REDIRECT_FIELD_NAME not in request.GET and REDIRECT_FIELD_NAME not in request.POST):
            context[REDIRECT_FIELD_NAME] = reverse('admin:twofactor_code', current_app=self.name)
        context.update(extra_context or {})

        from mighty.applications.twofactor.forms import TwoFactorChoicesForm
        defaults = {
            'extra_context': context,
            'authentication_form': TwoFactorChoicesForm,
            'success_url': reverse('admin:twofactor_code'),
            'template_name': self.login_template or 'admin/choices.html',
        }
        request.current_app = self.name
        from mighty.applications.twofactor.views import LoginStepChoices
        return LoginStepChoices.as_view(**defaults)(request)

    def stepcode(self, request, extra_context=None):
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
            next_url=request.GET.get('next', ''),
            is_nav_sidebar_enabled=False,
        )
        if (REDIRECT_FIELD_NAME not in request.GET and REDIRECT_FIELD_NAME not in request.POST):
            context[REDIRECT_FIELD_NAME] = reverse('admin:index', current_app=self.name)
        context.update(extra_context or {})

        from mighty.applications.twofactor.forms import TwoFactorCodeForm
        defaults = {
            'extra_context': context,
            'authentication_form': TwoFactorCodeForm,
            'success_url': reverse('admin:index'),
            'template_name': self.login_template or 'admin/code.html',
        }
        request.current_app = self.name
        from mighty.applications.twofactor.views import LoginStepCode
        return LoginStepCode.as_view(**defaults)(request)


    def showurls_view(self, request, extra_context=None, **kwargs):
        from mighty.showurls import ShowUrls
        context = {
            **self.each_context(request),
            "urls": ShowUrls().get_urls(search=request.GET.get("search")),
        }
        return TemplateResponse(request, 'admin/show_urls.html', context)

    ##########################
    # Supervision
    ##########################
    def supervision_view(self, request, extra_context=None):
        services = {}
        for service, commands in supervision.items():
            services[service] = {'uptime': service_uptime(service, commands.get('uptime'))}
            services[service]['cpu'] = service_cpu(service, commands.get('cpu'))
            services[service]['memory'] = service_memory(service, commands.get('memory'))
        context = {
            **self.each_context(request),
            'supervision': _.supervision,
            'services': services,
            'enable_channel': conf.enable_channel,
        }
        return TemplateResponse(request, 'admin/supervision/supervision.html', context)

    def supervision_channel_view(self, request, extra_context=None):
        context = {**self.each_context(request),
            'supervision': _.supervision,
            #'groups': asyncio.run(channels_group('asgi::group:*')),
            #'users': asyncio.run(channels_group('specific.*')),
        }
        return TemplateResponse(request, 'admin/supervision/channel_list.html', context)

    def supervision_channelflushall_view(self, request, extra_context=None):
        #asyncio.run(flushdb())
        return redirect('admin:supervision_channel_list')

    def supervision_channeljoin_view(self, request, extra_context=None, **kwargs):
        room = kwargs.get('room')
        room_def = room.split(conf.Channel.delimiter)
        context = {**self.each_context(request),
            'supervision': _.supervision,
            'room': room,
            'room_def': room_def,
            'from': room_def[0],
            'to': room_def[1],
        }
        return TemplateResponse(request, 'admin/supervision/channel_detail.html', context)

    def get_urls(self):
        urls = super(AdminSite, self).get_urls()
        from django.urls import path
        my_urls = []
        if 'mighty.applications.twofactor' in settings.INSTALLED_APPS:
            logger.info("Login twofactor enable")
            my_urls.append(path('login/', self.stepsearch, name='twofactor_search'))
            my_urls.append(path('login/choices/', self.stepchoices, name='twofactor_choices'))
            my_urls.append(path('login/code/', self.stepcode, name='twofactor_code'))
        my_urls.append(path("showurls/", self.wrap(self.showurls_view), name="mighty_showurls"))
        if conf.enable_supervision:
            my_urls.append(path('supervision/', self.admin_view(self.supervision_view), name='supervision'))
            if conf.enable_channel:
                my_urls.append(path('supervision/channels/', self.admin_view(self.supervision_channel_view), name='supervision_channel_list'))
                my_urls.append(path('supervision/channels/flushall/', self.admin_view(self.supervision_channelflushall_view), name='supervision_channel_flushall'))
                my_urls.append(path('supervision/channels/join/<str:room>/', self.admin_view(self.supervision_channeljoin_view), name='supervision_channel_detail'))

        if len(conf.urls_admin_to_add):
            from django.utils.module_loading import import_string
            for app in conf.urls_admin_to_add:
                for url in app["urls"]:
                    view = import_string(url["view"])
                    my_urls.append(path(url["path"], self.admin_view(view.as_view() if hasattr(view, "as_view") else view), name=url["name"]))
        return my_urls + urls
