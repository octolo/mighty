from mighty.applications.logger import EnableLogger
from mighty.errors import BackendError
import os

class Reader(EnableLogger):
    pt_to_px = 1.3333333333333333
    metadata = {}
    writer = None
    reader = None

    def backend_error(self, msg):
        raise BackendError(msg)

    def __init__(self, file, *args, **kwargs):
        self.file = file
        self.filename = kwargs.get("filename", os.path.basename(file.name))
        self.extension = kwargs.get("extension", os.path.splitext(self.filename)[-1])
        for k,v in kwargs.items(): setattr(self, k, v)
        if kwargs.get("reader"): self.prepare_reader()
        if kwargs.get("writer"): self.prepare_writer()

    def prepare_reader(self):
        pass

    def prepare_writer(self):
        pass

    def get_meta_data(self):
        pass

    def copy_file(self, *args, **kwargs):
        pass