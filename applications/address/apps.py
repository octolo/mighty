from django.apps import AppConfig
from django.conf import settings
from mighty import over_config
from mighty.functions import setting

class Config:
    backend = 'mighty.applications.address.backends.geopy.SearchBackend'

    class Default:
        country = 'France'
        country_code = 'FR'

    class Key:
        google = setting('GOOGLE_API_ADDRESS')
        mapbox = setting('MAPBOX_ACCESS_TOKEN')

if hasattr(settings, 'ADDRESS'): over_config(Config, settings.ADDRESS)
class AddressConfig(AppConfig, Config):
    name = 'mighty.applications.address'
