from django.utils.decorators import method_decorator
from django.utils.module_loading import import_string
from django.views.decorators.csrf import csrf_exempt

from mighty.applications.messenger import (
    missive_backend_app,
    missive_backend_email,
    missive_backend_emailar,
    missive_backend_postal,
    missive_backend_postalar,
    missive_backend_sms,
    missive_backend_web,
)
from mighty.functions import url_domain
from mighty.models import Missive
from mighty.views import DetailView, JsonView


# Create your views here.
class EmailViewer(DetailView):
    model = Missive
    template_name = 'messenger/email_viewer.html'
    slug_url_kwarg = 'uid'
    slug_field = 'uid'

    def get_context_data(self, **kwargs):
        ct = super().get_context_data(**kwargs)
        ct['domain_url'] = url_domain('', http=True)
        return ct

    def get_template_names(self):
        obj = self.get_object()
        return obj.template or super().get_template_names()

@method_decorator(csrf_exempt, name='dispatch')
class WebhookMessenger(JsonView):
    backend_path = missive_backend_email()

    @property
    def backend(self):
        return import_string(self.backend_path + '.MissiveBackend')(missive={})

    def do_post(self, request, *args, **kwargs):
        return self.backend.on_webhook(request)

    def do_get(self, request, *args, **kwargs):
        return self.backend.on_webhook(request)


class WebhookEmailAR(WebhookMessenger):
    backend_path = missive_backend_emailar()


class WebhookPostal(WebhookMessenger):
    backend_path = missive_backend_postal()


class WebhookPostalAR(WebhookMessenger):
    backend_path = missive_backend_postalar()


class WebhookSMS(WebhookMessenger):
    backend_path = missive_backend_sms()


class WebhookWeb(WebhookMessenger):
    backend_path = missive_backend_web()


class WebhookApp(WebhookMessenger):
    backend_path = missive_backend_app()
