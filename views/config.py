from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, JsonResponse

from mighty.applications.nationality.apps import NationalityConfig
from mighty.applications.twofactor.apps import TwofactorConfig
from mighty.applications.user import get_form_fields
from mighty.apps import MightyConfig as conf
from mighty.functions import setting
from mighty.models import ConfigClient, ConfigSimple
from mighty.views.crud import DetailView, ListView
from mighty.views.template import TemplateView

base_config = {
    'base': {
        'logo': conf.logo,
        'email': TwofactorConfig.method.email,
        'sms': TwofactorConfig.method.sms,
        'basic': TwofactorConfig.method.basic,
        'languages': NationalityConfig.availables,
        'fields': get_form_fields(),
    }}
base_config.update(setting('BASE_CONFIG', {}))


# Return the base config of mighty
class Config(TemplateView):
    def get_config(self):
        return base_config

    def get_context_data(self, **kwargs):
        return self.get_config()

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, **response_kwargs)


# Return all configs in model ConfigClient
class ConfigListView(ListView):
    model = ConfigClient

    def get_queryset(self):
        return [ConfigClient.objects.filter(is_disable=False), ConfigSimple.objects.filter(is_disable=False)]

    def render_to_response(self, context):
        cfg = base_config
        if 'mighty.applications.nationality' in setting('INSTALLED_APPS'):
            from mighty.applications.nationality import conf_prefix_numbering
            cfg.update({'phones': conf_prefix_numbering()})
        for cfgs in context['object_list']:
            cfg.update({cfg.url_name: cfg.config for cfg in cfgs})
        return JsonResponse(cfg)


# Return a named Config
class ConfigDetailView(DetailView):
    model = ConfigClient

    def get_config(self):
        try:
            return ConfigClient.objects.get(url_name=self.kwargs.get('name'))
        except ConfigClient.DoesNotExist:
            return ConfigSimple.objects.get(url_name=self.kwargs.get('name'))

    def get_object(self, queryset=None):
        try:
            return self.get_config()
        except ObjectDoesNotExist:
            raise Http404

    def render_to_response(self, context):
        cfg = self.get_object()
        return JsonResponse({cfg.name: cfg.config})
