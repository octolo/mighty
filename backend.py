from mighty.applications.logger import EnableLogger
from mighty.apps import MightyConfig
from mighty.functions import setting, url_domain


class Backend(EnableLogger):
    in_error = False

    def setting(self, data):
        return setting(data)

    def url_domain(self, url):
        return url_domain(url)

    @property
    def domain(self):
        return MightyConfig.domain

    @property
    def base_url(self):
        return f'https://{self.domain}/'
