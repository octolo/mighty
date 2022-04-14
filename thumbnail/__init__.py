from mighty.applications.logger import EnableLogger
from mighty.thumbnail.pdf import ThumbnailBackend as ThumbnailPDF

class Thumbnail(EnableLogger):
    element = None
    formt = None
    alias = {
        "application/pdf": "pdf",
    }

    def __init__(self, element, formt):
        self.element = element
        self.formt = "thumbnail_"+self.get_alias(formt)

    def get_alias(self, formt):
        return self.alias[formt] if formt in self.alias else formt

    @property
    def base64(self):
        if hasattr(self, self.formt):
            return getattr(self, self.formt)(self.element).base64
        return None

    def thumbnail_pdf(self, element):
        return ThumbnailPDF(element)
