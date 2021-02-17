default_app_config = 'mighty.applications.address.apps.AddressConfig'

from django.utils.module_loading import import_string
from mighty.applications.address.apps import AddressConfig

def get_address_backend():
    return import_string(AddressConfig.backend)()

fields = ('address', 'complement', 'postal_code', 'locality', 'state', 'state_code', 'country', 'country_code', 'raw')