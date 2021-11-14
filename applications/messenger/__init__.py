default_app_config = 'mighty.applications.messenger.apps.MessengerConfig'

from django.conf import settings
from mighty.functions import get_backends
from mighty.applications.messenger.choices import MODE_EMAIL, MODE_SMS, MODE_POSTAL
from mighty.applications.messenger.apps import MessengerConfig as conf

def send_missive(missive):
    for backend, backend_path in get_backends([missive.backend], return_tuples=True, path_extend='.MissiveBackend', missive=missive):
        return backend.send()
    return False

def send_missive_type(**kwargs):
    from mighty.models import Missive
    missive = Missive(
        header_html=kwargs.get('header_html'),
        footer_html=kwargs.get('footer_html'),
        content_type=kwargs.get('content_type'),
        object_id=kwargs.get('object_id'),
        mode=kwargs.get('mode'),
        target=kwargs.get('target'),
        subject=kwargs.get('subject'),
        html=kwargs.get('html'),
        txt=kwargs.get('txt'),
        address=kwargs.get('address'),
        complement=kwargs.get('complement'),
        postal_code=kwargs.get('postal_code'),
        locality=kwargs.get('locality'),
        state=kwargs.get('state'),
        state_code=kwargs.get('state_code'),
        country=kwargs.get('country', 'France'),
        country_code=kwargs.get('country_code', 'FR'),
        raw=kwargs.get('raw'),
    )
    missive.attachments = kwargs.get('attachments')
    missive.save()
    return missive

def send_email(**kwargs):
    return send_missive_type(**kwargs, mode=MODE_EMAIL)

def send_sms(**kwargs):
    return send_missive_type(**kwargs, mode=MODE_SMS, html="empty_for_sms")

def send_postal(**kwargs):
    return send_missive_type(**kwargs, mode=MODE_POSTAL, txt="empty_for_postal")

# ** kwargs:
#    -- mode
#    -- status
#    -- priority
#    -- target
#    -- service
#    -- denomination
#    -- header_html
#    -- footer_html
#    -- html
#    -- txt
# notify("sujet de la notification", model.get_content_type(), model.id, mode="email", target="contact@domain.com", txt="mon text", html="mon text html")
def notify(subject, content_type, object_id, **kwargs):
    from mighty.models import Notification
    notif = Notification(**kwargs, subject=subject, content_type=content_type, object_id=object_id)
    notif.save()

def missive_backend_postal():
    return settings.MISSIVE_BACKEND_POSTAL if hasattr(settings, 'MISSIVE_BACKEND_POSTAL') else conf.missive_backends

def missive_backend_postalar():
    return settings.MISSIVE_BACKEND_POSTALAR if hasattr(settings, 'MISSIVE_BACKEND_POSTALAR') else conf.missive_backends

def missive_backend_email():
    return settings.MISSIVE_BACKEND_EMAIL if hasattr(settings, 'MISSIVE_BACKEND_EMAIL') else conf.missive_backends

def missive_backend_emailar():
    return settings.MISSIVE_BACKEND_EMAILAR if hasattr(settings, 'MISSIVE_BACKEND_EMAILAR') else conf.missive_backends

def missive_backend_sms():
    return settings.MISSIVE_BACKEND_SMS if hasattr(settings, 'MISSIVE_BACKEND_SMS') else conf.missive_backends

def missive_backend_web():
    return settings.MISSIVE_BACKEND_WEB if hasattr(settings, 'MISSIVE_BACKEND_WEB') else conf.missive_backends

def missive_backend_app():
    return settings.MISSIVE_BACKEND_APP if hasattr(settings, 'MISSIVE_BACKEND_APP') else conf.missive_backends