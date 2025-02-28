from geopy import geocoders

from mighty.applications.address.backends import SearchBackend
from mighty.apps import MightyConfig


class SearchBackend(SearchBackend):
    service_default = 'nominatim'
    service_cache = None

    def get_address(self, data):
        address = self.get_dict('geopy')
        if data:
            address['raw'] = data.address
            address['latitude'] = data.latitude,
            address['longitude'] = data.longitude,
        return address

    @property
    def service(self):
        if not self.service_cache:
            service = geocoders.get_geocoder_for_service(self.service_default)
            self.service_cache = service(user_agent=MightyConfig.domain)
        return self.service_cache

    def get_location(self, input_str):
        location = self.service.geocode(input_str)
        return self.get_address(location) if location else False

    def get_list(self, input_str, offset=0, limit=15):
        location = self.get_location(input_str)
        return [location] if location else []
