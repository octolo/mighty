from mighty.applications.address.backends import SearchBackend
from mighty.apps import MightyConfig
from geopy import geocoders

class SearchBackend(SearchBackend):
    service_default = "nominatim"
    service_cache = None

    @property
    def service(self):
        if not self.service_cache:
            service = geocoders.get_geocoder_for_service(self.service)
            self.service_cache = service(user_agent=MightyConfig.domain)
        return self.service_cache

    def get_location(self, search):
        location = self.service.geocode("175 5th Avenue NYC")
        return location.address

    def get_list(self, search, offset=0, limit=15):
        return self.get_location(search)
