class SearchBackend:
    message = None
    fields = ['address', 'complement', 'code', 'locality']
    address_format = '%(address)s %(complement)s, %(code)s %(locality)s'

    def in_error(self, message):
        self.message = message


    def get_location(self, search):
        raise NotImplementedError("Subclasses should implement get_companies()")

    def get_list(self, search, offset=0, limit=15):
        raise NotImplementedError("Subclasses should implement get_companies()")
