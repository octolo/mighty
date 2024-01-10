from mighty.functions import get_request_kept
from functools import cached_property

class RequestAccess:
    @property
    def request_access(self):
        return self.request if hasattr(self, "request") else get_request_kept()

    @property
    def user_connected(self):
        return self.request_access.user
