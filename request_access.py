from mighty.functions import get_request_kept


class RequestAccess:
    @property
    def request_access(self):
        return self.request if hasattr(self, 'request') else get_request_kept()

    @property
    def user_connected(self):
        return self.request_access.user
