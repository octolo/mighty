from django.conf import settings
from django.contrib import admin
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import LoginView
from django.urls import reverse, resolve
from django.views.decorators.cache import never_cache
from django.template.response import TemplateResponse
from django.shortcuts import redirect

from mighty import translates as _
from mighty.apps import MightyConfig as conf
from mighty.functions import service_uptime, service_cpu, service_memory
from functools import update_wrapper

supervision = {
    'server': {
        'uptime': "cat /proc/uptime | awk '{ print $1}' | tr -d '\n'",
        'cpu': """cat /proc/loadavg | awk '{print $1"\\n"$2"\\n"$3}'""",
        'memory': "free | grep Mem | awk '{print $3/$2 * 100.0}' | tr -d ' '"
    }
}
supervision.update(getattr(settings, 'SUPERVISION', {}))

import asyncio
import aioredis
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
        if conf.supervision:
            my_urls.append(path('supervision/', self.admin_view(self.supervision_view), name='supervision'))
        if 'mighty.applications.chat' in settings.INSTALLED_APPS:
            my_urls.append(path('supervision/channels/', self.admin_view(self.supervision_channel_view), name='supervision_channel_list'))
            my_urls.append(path('supervision/channels/flushall/', self.admin_view(self.supervision_channelflushall_view), name='supervision_channel_flushall'))
            my_urls.append(path('supervision/channels/join/<str:room>/', self.admin_view(self.supervision_channeljoin_view), name='supervision_channel_detail'))
        return my_urls + urls