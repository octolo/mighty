from django.http import StreamingHttpResponse
from django.utils.text import get_valid_filename
from mighty.functions import make_searchable
import csv

class StreamingBuffer:
    def write(self, value): return value

class FileGenerator:
    filename = None
    items = []
    fields = ()
    ct_list = {
        "text/csv": "csv",
    }

    def __init__(self, *args, **kwargs):
        for name, data in kwargs.items():
            setattr(self, name, data)

    def iter_items_csv(self, items, pseudo_buffer):
        writer = csv.writer(pseudo_buffer, quoting=csv.QUOTE_ALL)
        yield writer.writerow(self.fields)
        for item in items:
            yield writer.writerow(item)

    def get_by_content_type(self, ct="text/csv", response="http"):
        return getattr(self, "response_%s" % response)(self.ct_list[ct])

    def get_by_format(self, ct="csv", response="http"):
        return getattr(self, "response_%s" % response)(ct)

    def get_filename(self, ct):
        return "%s.%s" % (get_valid_filename(make_searchable(self.filename)), ct)

    def get_content(self, ct, buffer):
        items_method = "iter_items_%s" % ct
        getattr(self, items_method)(self.items, buffer)

    def response_file(self, ct):
        items_method = "iter_items_%s" % ct
        getattr(self, items_method)(self.items, open(self.get_filename(ct), 'w'))
        
    def response_http(self, ct):
        ct_fmt = {v: k for k, v in self.ct_list.items()}[ct]
        response = StreamingHttpResponse(
            streaming_content=(self.get_content(ct, StreamingBuffer())),
            content_type=ct_fmt)
        response['Content-Disposition'] = 'attachment;filename='+self.get_filename(ct)
        return response
