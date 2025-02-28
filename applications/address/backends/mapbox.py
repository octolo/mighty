import requests

from mighty.applications.address.apps import AddressConfig
from mighty.applications.address.backends import SearchBackend


class SearchBackend(SearchBackend):
    ACCESS_TOKEN = AddressConfig.Key.mapbox
    url = 'https://api.mapbox.com/geocoding/v5/mapbox.places/%s.json?access_token=%s'

    def get_address(self, data):
        address = self.get_dict('mapbox')
        address['addr_backend_id'] = data.get('id')
        address['raw'] = data.get('place_name')
        address['address'] = ' '.join([data.get('address', ''), data.get('text', '')])
        geometry = data.get('geometry')
        if geometry:
            address['longitude'] = geometry['coordinates'][0]
            address['latitude'] = geometry['coordinates'][1]
        for component in data.get('context', []):
            ctx = component['id'].split('.')[0]
            if ctx == 'postcode':
                address['postal_code'] = component.get('text')
            elif ctx == 'place':
                address['locality'] = component.get('text')
            elif ctx == 'region':
                address['state'] = component.get('text')
            elif ctx == 'country':
                address['country'] = component.get('text')
                address['country_code'] = component.get('short_code')
            else:
                continue
        return address

    def service(self, url):
        return requests.get(url).json()

    def get_url(self, input_str):
        url = self.url % (input_str, self.ACCESS_TOKEN)
        if self.config.proximity:
            return url + '&proximity=' + self.config.proximity
        return url

    def get_location(self, input_str):
        url = self.get_url(input_str)
        location = self.service(url)
        return self.get_address(location['features'][0])

    def get_list(self, input_str, offset=0, limit=15):
        url = self.get_url(input_str)
        location = self.service(url)
        return [self.get_address(address) for address in location['features']]
