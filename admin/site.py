from django.conf import settings
from django.contrib import admin
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import LoginView
from django.urls import reverse, resolve
from django.views.decorators.cache import never_cache
from django.template.response import TemplateResponse

from mighty import translates as _
from mighty.apps import MightyConfig as conf
from mighty.functions import service_uptime, service_cpu, service_memory
from functools import update_wrapper

supervision = {
    'server': {
        'uptime': "cat /proc/uptime | awk '{ print $1}' | tr -d '\n'",
        'cpu': "ps -axo %cpu --no-headers | grep -v \" 0.0\" | tr -d ' '",
        'memory': "free | grep Mem | awk '{print $3/$2 * 100.0}' | tr -d ' '"
    }
}
supervision.update(getattr(settings, 'SUPERVISION', {}))

import asyncio
import aioredis
async def channels_group(pattern):
    redis = await aioredis.create_redis_pool('redis://localhost')
    keys = await redis.keys(pattern, encoding='utf-8')
    channels = {key: await redis.ttl(key) for key in keys}
    redis.close()
    await redis.wait_closed()
    return channels

async def flushdb():
    redis = await aioredis.create_redis_pool('redis://localhost')
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
        context = {**self.each_context(request), 
            'supervision': _.supervision,
            'services': services,
            'chat': 'mighty.applications.chat' in settings.INSTALLED_APPS
        }
        return TemplateResponse(request, 'admin/supervision.html', context)

    def supervision_chat_view(self, request, extra_context=None):
        fdb = request.GET.get('flushdb')
        if fdb: asyncio.run(flushdb())
        context = {**self.each_context(request),
            'supervision': _.supervision,
            'groups': asyncio.run(channels_group('asgi::group*')),
            'users': asyncio.run(channels_group('specific.*')),
        }
        return TemplateResponse(request, 'admin/chat.html', context)

    def get_urls(self):
        urls = super(AdminSite, self).get_urls()
        from django.urls import path
        my_urls = []
        if conf.supervision:
            my_urls.append(path('supervision/', self.admin_view(self.supervision_view), name='mighty_supervision'))
        if 'mighty.applications.chat' in settings.INSTALLED_APPS:
            my_urls.append(path('supervision/chat/', self.admin_view(self.supervision_chat_view), name='mighty_supervision_chat'))
        return my_urls + urls