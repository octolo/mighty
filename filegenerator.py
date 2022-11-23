from django.http import StreamingHttpResponse, HttpResponse
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
        "application/vnd.ms-excel": "xls",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    }
    row = 0
    col = 0

    @property
    def reverse_ct_list(self):
        return {v: k for k, v in self.ct_list.items()}

    def __init__(self, *args, **kwargs):
        for name, data in kwargs.items():
            setattr(self, name, data)

    @property
    def iter_rows(self):
        yield self.fields
        for row in self.items:
            yield row

    def get_by_content_type(self, ct="text/csv", response="http"):
        return getattr(self, "response_%s" % response)(self.ct_list[ct])

    def get_by_format(self, ct="csv", response="http"):
        return getattr(self, "response_%s" % response)(ct)

    def get_filename(self, ct):
        return "%s.%s" % (get_valid_filename(make_searchable(self.filename)), ct)

    def response_file(self, ct):
        items_method = "iter_items_%s" % ct
        getattr(self, items_method)(self.items, open(self.get_filename(ct), 'w'))

    # EXCEL
    def iter_items_xls(self, items, ws):
        for row in self.iter_rows:
            ws.append(row)

    def http_xlsx(self, ext, ct):
        return self.http_xls(ext, ct)

    def http_xls(self, ext, ct):
        from openpyxl import Workbook
        from tempfile import NamedTemporaryFile
        wb = Workbook()
        ws = wb.active
        self.iter_items_xls(self.items, ws)
        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            tmp.seek(0)
            stream = tmp.read()
        response = HttpResponse(content=stream, content_type=ct)
        response['Content-Disposition'] = 'attachment;filename='+self.get_filename(ext)
        return response

    # CSV
    def iter_items_csv(self, items, pseudo_buffer):
        writer = csv.writer(pseudo_buffer, quoting=csv.QUOTE_ALL)
        for item in self.iter_rows:
            yield writer.writerow(item)

    def http_csv(self, ext, ct):
        response = StreamingHttpResponse(
            streaming_content=self.iter_items_csv(self.items, StreamingBuffer()),
            content_type=ct)
        response['Content-Disposition'] = 'attachment;filename='+self.get_filename(ext)
        return response

    def response_http(self, ct):
        return getattr(self, "http_"+ct)(ct, self.reverse_ct_list[ct])
