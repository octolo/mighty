from mighty.applications.address.backends import SearchBackend
from mighty.applications.address.apps import AddressConfig
import requests

class SearchBackend(SearchBackend):
    API_KEY = AddressConfig.Key.google
    url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&lang=%s&key=%s"

    def get_address(self, data):
        address = self.get_dict('google')
        address['raw'] = data.get('formatted_address')
        address['addr_backend_id'] = data.get('place_id')
        geometry = data.get('geometry')
        if geometry:
            address['longitude'] = geometry['location']['lng']
            address['latitude'] = geometry['location']['lat']
        number = street = ''
        for component in address['address_components']:
            if 'street_number' in component['types']:
                number = component['long_name']
            elif 'route' in component['types']:
                street = component['long_name']
            elif 'country' in component['types']:
                address['country'] = component['long_name']
                address['country_code'] = component.get('short_name')
            elif 'postal_code' in component['types']:
                address['postal_code'] = component['long_name']
            elif 'locality' in component['types']:
                address['locality'] = component['long_name']
            elif 'postal_town' in component['types']:
                address['locality'] = component['long_name']
            else:
                continue
        address['address'] = street + ' ' + number
        return address

    def service(self, url):
        return requests.get(url).json()

    def get_url(self, input_str, lang='en'):
        return self.url % (input_str, lang, self.API_KEY)

    def get_location(self, input_str):
        url = self.get_url(input_str)
        location = self.service(url)
        return self.get_address([0])
        
    def get_list(self, input_str, offset=0, limit=15):
        url = self.get_url(input_str)
        location = self.service(url)
        return [self.get_address(address) for address in location['results']]
        
