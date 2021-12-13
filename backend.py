from mighty.apps import MightyConfig
from mighty.applications.logger import EnableLogger

import logging
logger = logging.getLogger(__name__)

class Backend(EnableLogger):
    in_error = False

    @property
    def domain(self):
        return MightyConfig.domain

    @property
    def base_url(self):
        return "https://%s/" % self.domain
        