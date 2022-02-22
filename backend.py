from mighty.apps import MightyConfig
from mighty.applications.logger import EnableLogger

class Backend(EnableLogger):
    in_error = False

    @property
    def domain(self):
        return MightyConfig.domain

    @property
    def base_url(self):
        return "https://%s/" % self.domain
        