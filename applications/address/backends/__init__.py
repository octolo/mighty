from mighty.applications.address.apps import AddressConfig


class SearchBackend:
    message = None
    fields = ['address', 'complement', 'code', 'locality']
    address_format = '%(address)s %(complement)s, %(code)s %(locality)s'

    @property
    def config(self):
        return AddressConfig

    def in_error(self, message):
        self.message = message

    def get_dict(self, source):
        return {
            'raw': None,
            'id': None,
            'address': None,
            'complement': None,
            'locality': None,
            'postal_code': None,
            'state': None,
            'state_code': None,
            'country': None,
            'country_code': None,
            'cedex': None,
            'cedex_code': None,
            'special': None,
            'index': None,
            'latitude': None,
            'longitude': None,
            'source': source,
        }

    def get_location(self, search):
        raise NotImplementedError('Subclasses should implement get_companies()')

    def get_list(self, search, offset=0, limit=10):
        raise NotImplementedError('Subclasses should implement get_companies()')

    def give_list(self, search, offset=0, limit=10):
        address_list = self.get_list(search, offset, limit)
        if address_list:
            return (
                address_list[offset:limit]
                if len(address_list) > limit
                else address_list
            )
        return []
