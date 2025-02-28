from mighty.applications.logger import EnableLogger


class ThumbnailBackend(EnableLogger):
    element = None

    def __init__(self, element):
        self.element = element

    @property
    def base64(self):
        raise NotImplementedError('base64 not implemented')
