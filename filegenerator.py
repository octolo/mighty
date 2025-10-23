import csv
import os
import pathlib
import shutil
import tempfile
from tempfile import NamedTemporaryFile

import pdfkit
from django.conf import settings
from django.http import HttpResponse, StreamingHttpResponse
from django.template import Context, Template
from django.template.loader import get_template
from django.utils.text import get_valid_filename
from openpyxl import Workbook

from mighty.apps import MightyConfig as conf
from mighty.functions import make_searchable


class StreamingBuffer:
    def write(self, value):
        return value


class FileGenerator:
    filename = None
    items = []
    fields = ()
    ct_list = {
        'text/csv': 'csv',
        'application/vnd.ms-excel': 'xls',
        'application/vnd.ms-excel': 'excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
        'application/pdf': 'pdf',
        'text/html': 'html',
        'application/json': 'json',
        'application/xml': 'xml',
        'text/plain': 'txt',
    }
    row = 0
    col = 0

    @property
    def reverse_ct_list(self):
        return {v: k for k, v in self.ct_list.items()}

    def __init__(self, *args, **kwargs):
        print(kwargs.get('queryset'))
        for name, data in kwargs.items():
            setattr(self, name, data)

    @property
    def iter_rows(self):
        yield self.fields
        yield from self.items

    def get_by_content_type(self, ct='text/csv', response='http'):
        return getattr(self, f'response_{response}')(self.ct_list[ct])

    def get_by_format(self, ct='csv', response='http'):
        return getattr(self, f'response_{response}')(ct)

    def get_filename(self, ct):
        return f'{get_valid_filename(make_searchable(self.filename))}.{ct}'

    def response_file(self, ct):
        items_method = f'iter_items_{ct}'
        getattr(self, items_method)(
            self.items, open(self.get_filename(ct), 'w', encoding='utf-8')
        )

    # EXCEL
    def iter_items_xls(self, items, ws):
        for row in self.iter_rows:
            ws.append(row)

    def file_xlsx(self, ext, ct):
        return self.file_xls(ext, ct)

    def file_xls(self, ext, ct):
        wb = Workbook()
        ws = wb.active
        self.iter_items_xls(self.items, ws)
        tmp = open(self.get_filename(ext), 'rb')
        wb.save(tmp.name)
        return tmp

    def http_excel(self, ext, ct):
        return self.http_xls('xlsx', ct)

    def http_xlsx(self, ext, ct):
        return self.http_xls(ext, ct)

    def http_xls(self, ext, ct):
        wb = Workbook()
        ws = wb.active
        self.iter_items_xls(self.items, ws)
        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            tmp.seek(0)
            stream = tmp.read()
        response = HttpResponse(content=stream, content_type=ct)
        response['Content-Disposition'] = (
            'attachment;filename=' + self.get_filename(ext)
        )
        return response

    # CSV
    def iter_stream_csv(self, items, pseudo_buffer):
        writer = csv.writer(pseudo_buffer, quoting=csv.QUOTE_ALL)
        for item in self.iter_rows:
            yield writer.writerow(item)

    def iter_items_csv(self, items, pseudo_buffer, stream=True):
        writer = csv.writer(pseudo_buffer, quoting=csv.QUOTE_ALL)
        for item in self.iter_rows:
            writer.writerow(item)

    def file_csv(self, ext, ct=None):
        tmp = open(self.get_filename(ext), 'w', encoding='utf-8')
        self.iter_items_csv(self.items, tmp, False)
        tmp.close()
        return open(self.get_filename(ext), 'rb')

    def http_csv(self, ext, ct):
        response = StreamingHttpResponse(
            streaming_content=self.iter_stream_csv(
                self.items, StreamingBuffer()
            ),
            content_type=ct,
        )
        response['Content-Disposition'] = (
            'attachment;filename=' + self.get_filename(ext)
        )
        return response

    # PDF
    def iter_items_pdf(self, items):
        headers = ''.join(f'<th>{field}</th>' for field in self.fields)
        rows = ''.join(
            f'<tr>{"".join(f"<td>{i if i is not None else ''}</td>" for i in item)}</tr>'
            for item in items
        )
        return f'<table><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table>'

    def generate_pdf_from_html(self, output_path=None):
        from datetime import datetime

        import pdfkit

        html_string = Template(self.html).render(
            Context({
                'table': self.iter_items_pdf(self.items),
                'items': self.items,
                'document_name': self.filename,
                'queryset': self.queryset,
            })
        )
        # Date du jour formatée
        today = datetime.today().strftime('%d/%m/%Y')

        # Texte de pied de page avec pagination
        footer_text = (
            f'Octolo certifié en date du {today} - Page [page] sur [topage]'
        )

        # Options wkhtmltopdf
        options = {
            'page-size': 'A4',
            'orientation': 'Landscape',
            'margin-top': '20mm',
            'margin-bottom': '20mm',
            'margin-left': '20mm',
            'margin-right': '20mm',
            'encoding': 'UTF-8',
            'enable-local-file-access': None,
            'footer-center': footer_text,
            'footer-font-size': '10',
            'footer-line': '',  # Ligne de séparation (optionnel)
        }
        return pdfkit.from_string(html_string, output_path, options=options)

    def file_pdf(self, ext, ct):
        return self.generate_pdf_from_html(output_path=self.get_filename('pdf'))

    def http_pdf(self, ext, ct):
        pdf_bytes = self.generate_pdf_from_html(False)
        print('-------------------')
        print('filename', self.get_filename('pdf'))
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = (
            f'inline; filename={self.get_filename("pdf")}'
        )
        return response

    def response_file(self, ct):
        return getattr(self, 'file_' + ct)(ct, self.reverse_ct_list[ct])

    def response_http(self, ct):
        return getattr(self, 'http_' + ct)(ct, self.reverse_ct_list[ct])


def generate_pdf(**kwargs):
    _header_enable, _footer_enable = False, False
    file_name = kwargs.get('file_name', False)
    options = kwargs.get('options', conf.pdf_options)
    header = kwargs.get('header', False)
    footer = kwargs.get('footer', False)
    context = kwargs.get('context', {})
    content = kwargs.get('content', False)
    content_html = kwargs.get('content_html', False)
    as_string = kwargs.get('as_string', False)
    context.update({
        'static': os.path.abspath(settings.STATIC_ROOT),
    })

    # header
    if header:
        header_tpl = kwargs.get(
            'conf_header',
            get_template(conf.pdf_header).render({'header': header}),
        )
        context.update({'header_html': header})
        header_html = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
        header_html.write(
            Template(header_tpl).render(Context(context)).encode('utf-8')
        )
        header_html.close()
        header = header_html
        options['--header-html'] = header_html.name

    if footer:
        footer_tpl = kwargs.get(
            'conf_footer',
            get_template(conf.pdf_footer).render({'footer': footer}),
        )
        context.update({'footer_html': footer})
        footer_html = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
        footer_html.write(
            Template(footer_tpl).render(Context(context)).encode('utf-8')
        )
        footer_html.close()
        footer = footer_html
        options['--footer-html'] = footer_html.name

    if (content or content_html) and file_name:
        tmp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=True)
        if content_html:
            content_html = Template(content_html).render(Context(context))
        else:
            content_html = get_template(content).render(context)
        content_tpl = kwargs.get(
            'conf_content',
            get_template(conf.pdf_content).render({'content': content_html}),
        )
        content_html = Template(content_tpl).render(Context(context))
        pdfkit.from_string(content_html, tmp_pdf.name, options=options)
        path_tmp = tmp_pdf.name
        valid_file_name = get_valid_filename(file_name)
        final_pdf = tempfile.gettempdir() + '/' + valid_file_name
        shutil.copyfile(path_tmp, final_pdf)

    # a verifier
    if footer:
        pathlib.Path(footer_html.name).unlink()
    if header:
        pathlib.Path(header_html.name).unlink()
    if as_string:
        tmp_pdf.close()
        pathlib.Path(final_pdf).unlink()
        return content_html
    return final_pdf, tmp_pdf


# def remove_tmpdf(files):
#    for f in files:
#        if hasattr(f, "close"):
#            f.close()
#        #os.remove(f.)
