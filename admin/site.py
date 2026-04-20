import logging
from functools import update_wrapper

from django.conf import settings
from django.contrib import admin
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from mighty import translates as _
from mighty.apps import MightyConfig as conf
from mighty.functions import service_cpu, service_memory, service_uptime

logger = logging.getLogger(__name__)

supervision = {
    'server': {
        'uptime': "cat /proc/uptime | awk '{ print $1}' | tr -d '\n'",
        'cpu': """cat /proc/loadavg | awk '{print $1"\\n"$2"\\n"$3}'""",
        'memory': "free | grep Mem | awk '{print $3/$2 * 100.0}' | tr -d ' '",
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
        extra_context['urls_admin_to_add'] = conf.urls_admin_to_add
        return super().index(request, extra_context=extra_context)

    def wrap(self, view):
        def wrapper(*args, **kwargs):
            return self.admin_view(view)(*args, **kwargs)

        wrapper.model_admin = self
        return update_wrapper(wrapper, view)

    def showurls_view(self, request, extra_context=None, **kwargs):
        from mighty.showurls import ShowUrls

        context = {
            **self.each_context(request),
            'urls': ShowUrls().get_urls(search=request.GET.get('search')),
        }
        return TemplateResponse(request, 'admin/show_urls.html', context)

    ##########################
    # Supervision
    ##########################
    def supervision_view(self, request, extra_context=None):
        services = {}
        for service, commands in supervision.items():
            services[service] = {
                'uptime': service_uptime(service, commands.get('uptime'))
            }
            services[service]['cpu'] = service_cpu(service, commands.get('cpu'))
            services[service]['memory'] = service_memory(
                service, commands.get('memory')
            )
        context = {
            **self.each_context(request),
            'supervision': _.supervision,
            'services': services,
            'enable_channel': conf.enable_channel,
        }
        return TemplateResponse(
            request, 'admin/supervision/supervision.html', context
        )

    def supervision_channel_view(self, request, extra_context=None):
        context = {
            **self.each_context(request),
            'supervision': _.supervision,
            # 'groups': asyncio.run(channels_group('asgi::group:*')),
            # 'users': asyncio.run(channels_group('specific.*')),
        }
        return TemplateResponse(
            request, 'admin/supervision/channel_list.html', context
        )

    def supervision_channelflushall_view(self, request, extra_context=None):
        # asyncio.run(flushdb())
        return redirect('admin:supervision_channel_list')

    def supervision_channeljoin_view(
        self, request, extra_context=None, **kwargs
    ):
        room = kwargs.get('room')
        room_def = room.split(conf.Channel.delimiter)
        context = {
            **self.each_context(request),
            'supervision': _.supervision,
            'room': room,
            'room_def': room_def,
            'from': room_def[0],
            'to': room_def[1],
        }
        return TemplateResponse(
            request, 'admin/supervision/channel_detail.html', context
        )

    def get_urls(self):
        urls = super().get_urls()
        from django.urls import path

        my_urls = [
            path(
                'showurls/',
                self.wrap(self.showurls_view),
                name='mighty_showurls',
            )
        ]
        if conf.enable_supervision:
            my_urls.append(
                path(
                    'supervision/',
                    self.admin_view(self.supervision_view),
                    name='supervision',
                )
            )
            if conf.enable_channel:
                my_urls.extend((
                    path(
                        'supervision/channels/',
                        self.admin_view(self.supervision_channel_view),
                        name='supervision_channel_list',
                    ),
                    path(
                        'supervision/channels/flushall/',
                        self.admin_view(self.supervision_channelflushall_view),
                        name='supervision_channel_flushall',
                    ),
                    path(
                        'supervision/channels/join/<str:room>/',
                        self.admin_view(self.supervision_channeljoin_view),
                        name='supervision_channel_detail',
                    ),
                ))

        if len(conf.urls_admin_to_add):
            from django.utils.module_loading import import_string

            for app in conf.urls_admin_to_add:
                for url in app['urls']:
                    view = import_string(url['view'])
                    my_urls.append(
                        path(
                            url['path'],
                            self.admin_view(
                                view.as_view()
                                if hasattr(view, 'as_view')
                                else view
                            ),
                            name=url['name'],
                        )
                    )
        return my_urls + urls
