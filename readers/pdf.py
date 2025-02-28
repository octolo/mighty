from django.core.files.uploadedfile import InMemoryUploadedFile
from PyPDF2 import PdfReader, PdfWriter

from mighty.readers.reader import Reader


class ReaderPDF(Reader):
    pages = []

    def prepare_writer(self):
        self.writer = PdfWriter()
        return self.writer

    def prepare_reader(self):
        self.reader = PdfReader(self.file if type(self.file) == InMemoryUploadedFile else self.file.name)
        return self.reader

    def get_meta_data(self):
        self.metadata = {}
        for k, v in self.reader.metadata.items():
            key = k.replace('/', '').lower()
            if isinstance(v, (str, int)):
                self.metadata[key] = v
        self.metadata['pages'] = []
        for page in self.reader.pages:
            self.metadata['pages'].append(self.get_page_data(page))
        self.metadata['nbpages'] = len(self.metadata['pages'])
        return self.metadata

    def get_page_data(self, page):
        return {
            'width_pt': round(float(page.mediabox.width), 2),
            'height_pt': round(float(page.mediabox.height), 2),
            'width_px': self.convert(page.mediabox.width, 'pt', 'px'),
            'height_px': self.convert(page.mediabox.height, 'pt', 'px'),
            # "images": len(page.images),
            'orientation': self.get_orientation(page),
        }

    def get_orientation(self, page):
        deg = page.get('/Rotate')
        mb = page.mediabox
        if mb.right - mb.left > mb.top - mb.bottom:
            return 'landscape' if deg in [0, 180, None] else 'portrait'
        return 'portrait' if deg in [0, 180, None] else 'landscape'

    def page_add_before(self, *args, **kwargs):
        pass

    def page_add_after(self, *args, **kwargs):
        pass

    def copy_file(self, *args, **kwargs):
        for page in reader.pages:
            self.page_add_before(page, *args, **kwargs)
            writer.add_page(page)
            self.page_add_after(page, *args, **kwargs)

        with open('smaller-new-file.pdf', 'wb') as fp:
            writer.write(fp)
