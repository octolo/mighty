from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect
from django.utils.text import capfirst
from django.urls import reverse, resolve
from django.views.decorators.cache import never_cache
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.utils.translation import gettext

from mighty import translates as _
from mighty.apps import MightyConfig as conf
from mighty.functions import service_uptime, service_cpu, service_memory, make_searchable
from functools import update_wrapper
import logging, asyncio, aioredis
logger = logging.getLogger(__name__)

supervision = {
    'server': {
        'uptime': "cat /proc/uptime | awk '{ print $1}' | tr -d '\n'",
        'cpu': """cat /proc/loadavg | awk '{print $1"\\n"$2"\\n"$3}'""",
        'memory': "free | grep Mem | awk '{print $3/$2 * 100.0}' | tr -d ' '"
    }
}
supervision.update(getattr(settings, 'SUPERVISION', {}))

async def channels_group(pattern):
    redis = await aioredis.create_redis_pool(settings.CHANNEL_LAYERS['default']['CONFIG']['hosts'][0])
    keys = await redis.keys(pattern, encoding='utf-8')
    channels = {key.replace(pattern[:-1], ''): await redis.ttl(key) for key in keys}
    redis.close()
    await redis.wait_closed()
    return channels

async def flushdb():
    redis = await aioredis.create_redis_pool(settings.CHANNEL_LAYERS['default']['CONFIG']['hosts'][0])
    await redis.flushdb()
    redis.close()
    await redis.wait_closed()

class AdminSite(admin.AdminSite):
    site_header = conf.site_header
    index_title = conf.index_title

    def _build_multi_app_dict(self, request, label=None):
        """
        Build the app dictionary. The optional `label` parameter filters models
        of a specific app.
        """
        multi_app_dict = {}
        if label:
            models = {m: m_a for m, m_a in self._registry.items()
                    if m._meta.app_label == label}
        else:
            models = self._registry
        
        for model, model_admin in models.items():
            app_label = model._meta.app_label
            app_config = apps.get_app_config(app_label)
            logger.info(app_config)    
            if hasattr(app_config, 'multi_apps'):    
                has_module_perms = model_admin.has_module_permission(request)
                if not has_module_perms:
                    continue
                perms = model_admin.get_model_perms(request)

                # Check whether user has any perm for this module.
                # If so, add the module to the model_list.
                if True not in perms.values():
                    continue

                info = (app_label, model._meta.model_name)
                app_parent = self.get_parent_app(app_config, model._meta.object_name)
                model_dict = {
                    'name': capfirst(model._meta.verbose_name_plural),
                    'object_name': model._meta.object_name,
                    'perms': perms,
                    'admin_url': None,
                    'add_url': None,
                }
                if perms.get('change') or perms.get('view'):
                    model_dict['view_only'] = not perms.get('change')
                    try:
                        model_dict['admin_url'] = reverse('admin:%s_%s_changelist' % info, current_app=self.name)
                    except NoReverseMatch:
                        pass
                if perms.get('add'):
                    try:
                        model_dict['add_url'] = reverse('admin:%s_%s_add' % info, current_app=self.name)
                    except NoReverseMatch:
                        pass

                if app_label not in multi_app_dict:
                    multi_app_dict[app_label] = {
                        'name': apps.get_app_config(app_label).verbose_name,
                        'app_label': app_label,
                        'app_url': reverse(
                            'admin:app_list',
                            kwargs={'app_label': app_label},
                            current_app=self.name,
                        ),
                        'has_module_perms': has_module_perms,
                        'apps': {},
                    }

                if app_parent in multi_app_dict[app_label]['apps']:
                    multi_app_dict[app_label]['apps'][app_parent]['models'].append(model_dict)
                else:
                    multi_app_dict[app_label]['apps'][app_parent] = {
                        'name': capfirst(app_parent),
                        'app_label': app_label,
                        'app_url': reverse(
                            'admin:app_list',
                            kwargs={'app_label': app_label},
                            current_app=self.name,
                        ),
                        'has_module_perms': has_module_perms,
                        'models': [model_dict],
                        'app_config': app_config,
                    }


        if label:
            return multi_app_dict.get(label)
        return multi_app_dict

    def get_parent_app(self, config, name):
        for app, models in config.multi_apps.items():
            if name in models:
                return app
        return 'others'
     
    def get_multi_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        multi_app_dict = self._build_multi_app_dict(request)
        multi_app_list = sorted(multi_app_dict.values(), key=lambda x: x['name'].lower())
        for idx, mapp in enumerate(multi_app_list):
            multi_app_list[idx]['apps'] = {key: mapp['apps'][key] for key in sorted(mapp['apps'].keys())}
            for app,value in mapp['apps'].items():
                multi_app_list[idx]['apps'][app]['models'].sort(key=lambda x: x['name'])
        return multi_app_list

    def app_index(self, request, app_label, extra_context=None):
        app_dict = self._build_app_dict(request, app_label)
        multi_app_dict = self._build_multi_app_dict(request, app_label)
        if not app_dict and not multi_app_dict:
            raise Http404('The requested admin page does not exist.')
        app_name = apps.get_app_config(app_label).verbose_name
        context = {
            **self.each_context(request),
            'title': gettext('%(app)s administration') % {'app': app_name},
            'app_label': app_label,
            'app_name': app_name,
            **(extra_context or {}),
        }
        request.current_app = self.name
        if multi_app_dict:
            multi_app_dict['apps'] = {key: multi_app_dict['apps'][key] for key in sorted(multi_app_dict['apps'].keys())}
            for app,value in multi_app_dict['apps'].items():
                multi_app_dict['apps'][app]['models'].sort(key=lambda x: x['name'])
            context['multi_app_list'] = [multi_app_dict]
            return TemplateResponse(request, self.app_index_template or [
                'admin/%s/multi_app_index.html' % app_label,
                'admin/multi_app_index.html'
            ], context)
        elif app_dict:
            app_dict['models'].sort(key=lambda x: x['name'])
            context['app_list'] = [app_dict]
            return TemplateResponse(request, self.app_index_template or [
                'admin/%s/app_index.html' % app_label,
                'admin/app_index.html'
            ], context)


    @never_cache
    def index(self, request, extra_context=None):
        """
        Display the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """
        app_list = []
        for app in self.get_app_list(request):
            app_config = apps.get_app_config(app['app_label'])
            if not hasattr(app_config, 'multi_apps'): app_list.append(app)

        multi_app_list = self.get_multi_app_list(request)
        context = {
            **self.each_context(request),
            'title': self.index_title,
            'app_list': app_list,
            'multi_app_list': multi_app_list,
            **(extra_context or {}),
        }
        request.current_app = self.name
        return TemplateResponse(request, self.index_template or 'admin/index.html', context)

    @never_cache
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
            next_url=request.GET.get('next', '')
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

    @never_cache
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
            next_url=request.GET.get('next', '')
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

    @never_cache
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
            next_url=request.GET.get('next', '')
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

    ##########################
    # Supervision
    ##########################
    def supervision_view(self, request, extra_context=None):
        services = {}
        for service, commands in supervision.items():
            services[service] = {'uptime': service_uptime(service, commands.get('uptime'))}
            services[service]['cpu'] = service_cpu(service, commands.get('cpu'))
            services[service]['memory'] = service_memory(service, commands.get('memory'))
        context = {**self.each_context(request), 'supervision': _.supervision, 'services': services}
        return TemplateResponse(request, 'admin/supervision.html', context)

    def supervision_channel_view(self, request, extra_context=None):
        context = {**self.each_context(request),
            'supervision': _.supervision,
            'groups': asyncio.run(channels_group('asgi::group:*')),
            'users': asyncio.run(channels_group('specific.*')),
        }
        return TemplateResponse(request, 'admin/channel_list.html', context)

    def supervision_channelflushall_view(self, request, extra_context=None):
        asyncio.run(flushdb())
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
        return TemplateResponse(request, 'admin/channel_detail.html', context)

    def get_urls(self):
        urls = super(AdminSite, self).get_urls()
        from django.urls import path
        my_urls = []
        if 'mighty.applications.twofactor' in settings.INSTALLED_APPS:
            my_urls.append(path('login/', self.stepsearch, name='twofactor_search'))
            my_urls.append(path('login/choices/', self.stepchoices, name='twofactor_choices'))
            my_urls.append(path('login/code/', self.stepcode, name='twofactor_code'))
        if conf.supervision:
            my_urls.append(path('supervision/', self.admin_view(self.supervision_view), name='supervision'))
            my_urls.append(path('supervision/channels/', self.admin_view(self.supervision_channel_view), name='supervision_channel_list'))
            my_urls.append(path('supervision/channels/flushall/', self.admin_view(self.supervision_channelflushall_view), name='supervision_channel_flushall'))
            my_urls.append(path('supervision/channels/join/<str:room>/', self.admin_view(self.supervision_channeljoin_view), name='supervision_channel_detail'))
        return my_urls + urls