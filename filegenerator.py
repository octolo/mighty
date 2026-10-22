import copy
import csv
import datetime
import json
import logging
import os
import pathlib
import shutil
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.contrib.staticfiles.finders import find as find_static_file
from django.http import HttpResponse, StreamingHttpResponse
from django.template import Context, Template
from django.template.loader import get_template
from django.utils import timezone
from django.utils.text import get_valid_filename
from openpyxl import Workbook
from weasyprint import HTML

from mighty.apps import MightyConfig as conf
from mighty.functions import make_searchable

logger = logging.getLogger(__name__)


class _HTMLDocumentParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.head = []
        self.body = []
        self.in_head = False

    @property
    def target(self):
        return self.head if self.in_head else self.body

    def handle_starttag(self, tag, attrs):
        if tag == 'head':
            self.in_head = True
        elif tag == 'body':
            return
        elif tag != 'html':
            self.target.append(self.get_starttag_text())

    def handle_startendtag(self, tag, attrs):
        self.target.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        if tag == 'head':
            self.in_head = False
        elif tag != 'html':
            self.target.append(f'</{tag}>')

    def handle_data(self, data):
        self.target.append(data)

    def handle_entityref(self, name):
        self.target.append(f'&{name};')

    def handle_charref(self, name):
        self.target.append(f'&#{name};')

    def handle_comment(self, data):
        self.target.append(f'<!--{data}-->')


def _split_html_document(source: str) -> tuple[str, str]:
    parser = _HTMLDocumentParser()
    parser.feed(source or '')
    return ''.join(parser.head), ''.join(parser.body)


def render_weasyprint_pdf(
    html_content: str,
    output_path: str | None = None,
    *,
    header_html: str | None = None,
    footer_html: str | None = None,
    options: dict | None = None,
    base_url: str | None = None,
) -> bytes | bool:
    """Render HTML, optional running header/footer, and page settings to PDF."""
    options = options or {}
    main_head, main_body = _split_html_document(html_content)
    header_head, header_body = _split_html_document(header_html or '')
    footer_head, footer_body = _split_html_document(footer_html or '')
    page_size = options.get('page-size', 'A4')
    orientation = str(options.get('orientation', 'Portrait')).lower()
    size = f'{page_size} {orientation}'
    margins = {
        side: options.get(f'margin-{side}', '0.75in')
        for side in ('top', 'right', 'bottom', 'left')
    }
    page_rules = [
        f'@page {{ size: {size}; margin: {margins["top"]} '
        f'{margins["right"]} {margins["bottom"]} {margins["left"]};'
    ]
    if header_body:
        page_rules.append(
            '@top-center { content: element(octolo-pdf-header); }'
        )
    footer_center = options.get('footer-center')
    if footer_body or footer_center:
        if footer_body:
            footer_content = 'element(octolo-pdf-footer)'
        else:
            footer_content = (
                json.dumps(str(footer_center), ensure_ascii=False)
                .replace('[page]', '" counter(page) "')
                .replace('[topage]', '" counter(pages) "')
            )
        footer_size = options.get('footer-font-size')
        footer_font = f' font-size: {footer_size}pt;' if footer_size else ''
        page_rules.append(
            f'@bottom-center {{ content: {footer_content};{footer_font} }}'
        )
    page_rules.append('}')
    timestamp = (
        timezone.localtime() if settings.USE_TZ else datetime.datetime.now()
    )
    substitutions = {
        'date': timestamp.strftime('%A, %B %d, %Y'),
        'isodate': timestamp.date().isoformat(),
        'time': timestamp.strftime('%H:%M'),
    }
    substitution_css = ''.join(
        f'.octolo-pdf-header .{name}::before,'
        f'.octolo-pdf-footer .{name}::before '
        f'{{ content: {json.dumps(value, ensure_ascii=False)}; }}'
        for name, value in substitutions.items()
    )
    document = (
        '<!doctype html><html><head>'
        f'{main_head}{header_head}{footer_head}'
        '<style>'
        + ''.join(page_rules)
        + '.octolo-pdf-header { position: running(octolo-pdf-header); }'
        + '.octolo-pdf-footer { position: running(octolo-pdf-footer); }'
        + '.octolo-pdf-header .page::before,'
        + '.octolo-pdf-footer .page::before,'
        + '.octolo-pdf-header .frompage::before,'
        + '.octolo-pdf-footer .frompage::before,'
        + '.octolo-pdf-header .sitepage::before,'
        + '.octolo-pdf-footer .sitepage::before { content: counter(page); }'
        + '.octolo-pdf-header .topage::before,'
        + '.octolo-pdf-footer .topage::before,'
        + '.octolo-pdf-header .sitepages::before,'
        + '.octolo-pdf-footer .sitepages::before { content: counter(pages); }'
        + substitution_css
        + '</style></head><body>'
        + (
            f'<div class="octolo-pdf-header">{header_body}</div>'
            if header_body
            else ''
        )
        + (
            f'<div class="octolo-pdf-footer">{footer_body}</div>'
            if footer_body
            else ''
        )
        + main_body
        + '</body></html>'
    )
    pdf_bytes = HTML(string=document, base_url=base_url).write_pdf()
    if output_path:
        Path(output_path).write_bytes(pdf_bytes)
        return True
    return pdf_bytes


class StreamingBuffer:
    def write(self, value):
        return value


def excel_cell_value(value):
    """Return a value openpyxl can write (Excel has no timezone support)."""
    if isinstance(value, datetime.datetime) and value.tzinfo is not None:
        return timezone.make_naive(value)
    if isinstance(value, datetime.time) and value.tzinfo is not None:
        return value.replace(tzinfo=None)
    if isinstance(value, (dict, list, tuple, set)):
        return str(value)
    return value


def _build_pdf_font_face_style():
    fonts = {}
    fonts.update(getattr(settings, 'PDFMAKER', {}).get('fonts', {}))
    fonts.update(getattr(settings, 'FONTS_FILES_WEASYPRINT', {}))

    rules = []
    for font_file, font_name in fonts.items():
        font_path = find_static_file(f'fonts/{font_file}')
        if not font_path:
            continue
        rules.extend([
            '@font-face {',
            f"  font-family: '{font_name}';",
            f"  src: url('file://{font_path}') format('truetype');",
            '  font-style: normal;',
            '  font-weight: 400;',
            '}',
        ])

    if not rules:
        return ''
    return '<style>' + '\n'.join(rules) + '</style>'


def _inject_font_style_in_head(html):
    style = _build_pdf_font_face_style()
    if not style:
        return html
    if '</head>' in html:
        return html.replace('</head>', f'{style}</head>', 1)
    return style + html


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
            ws.append([excel_cell_value(cell) for cell in row])

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

        html_string = Template(self.html).render(
            Context({
                'table': self.iter_items_pdf(self.items),
                'items': self.items,
                'document_name': self.filename,
                'queryset': self.queryset,
            })
        )
        html_string = _inject_font_style_in_head(html_string)
        # Date du jour formatée
        today = datetime.today().strftime('%d/%m/%Y')

        # Texte de pied de page avec pagination
        footer_text = (
            f'Octolo certifié en date du {today} - Page [page] sur [topage]'
        )

        # Page layout and footer for WeasyPrint.
        options = {
            'page-size': 'A4',
            'orientation': 'Landscape',
            'margin-top': '20mm',
            'margin-bottom': '20mm',
            'margin-left': '20mm',
            'margin-right': '20mm',
            'footer-center': footer_text,
            'footer-font-size': '10',
        }
        return render_weasyprint_pdf(
            html_string,
            output_path=output_path,
            options=options,
            base_url=str(settings.STATIC_ROOT),
        )

    def file_pdf(self, ext, ct):
        return self.generate_pdf_from_html(output_path=self.get_filename('pdf'))

    def http_pdf(self, ext, ct):
        pdf_bytes = self.generate_pdf_from_html(False)
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
    # Deep copy so we never mutate the shared conf.pdf_options dict across calls.
    options = copy.deepcopy(kwargs.get('options', conf.pdf_options))
    header = kwargs.get('header', False)
    footer = kwargs.get('footer', False)
    context = kwargs.get('context', {})
    content = kwargs.get('content', False)
    content_html = kwargs.get('content_html', False)
    as_string = kwargs.get('as_string', False)
    context.update({
        'static': os.path.abspath(settings.STATIC_ROOT),
    })

    header_html = None
    if header:
        header_tpl = kwargs.get(
            'conf_header',
            get_template(conf.pdf_header).render({'header': header}),
        )
        context.update({'header_html': header})
        header_html = Template(header_tpl).render(Context(context))
    else:
        options['margin-top'] = kwargs.get('margin_top') or options.get(
            'margin-top', '0.30in'
        )

    footer_html = None
    if footer:
        footer_tpl = kwargs.get(
            'conf_footer',
            get_template(conf.pdf_footer).render({'footer': footer}),
        )
        context.update({'footer_html': footer})
        footer_html = Template(footer_tpl).render(Context(context))
    else:
        options['margin-bottom'] = kwargs.get('margin_bottom') or options.get(
            'margin-bottom', '0.30in'
        )

    if (content or content_html) and file_name:
        tmp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=True)
        if content_html:
            content_html = Template(content_html).render(Context(context))
        else:
            content_html = get_template(content).render(context)
        content_tpl = kwargs.get(
            'conf_content',
            get_template(conf.pdf_content).render({
                'content': content_html,
                'body_lead': '<br/>' if header else '',
            }),
        )
        content_html = Template(content_tpl).render(Context(context))
        content_html = _inject_font_style_in_head(content_html)
        render_weasyprint_pdf(
            content_html,
            output_path=tmp_pdf.name,
            header_html=header_html,
            footer_html=footer_html,
            options=options,
            base_url=str(settings.STATIC_ROOT),
        )
        path_tmp = tmp_pdf.name
        valid_file_name = get_valid_filename(file_name)
        # Use a unique per-call temp directory to avoid collisions on a fixed
        # path like /tmp/<file_name> (which fails with PermissionError on
        # rootless/distroless containers when the file already exists).
        final_pdf = str(pathlib.Path(tempfile.mkdtemp()) / valid_file_name)
        shutil.copyfile(path_tmp, final_pdf)

    # a verifier
    if as_string:
        tmp_pdf.close()
        pathlib.Path(final_pdf).unlink()
        return content_html
    return final_pdf, tmp_pdf


DOCX_EXPORT_JUSTIFY_CSS = """<style type="text/css">
[align="justify"],
[style*="text-align: justify"],
[style*="text-align:justify"],
.text-justify,
.ql-align-justify,
.fr-text-justify {
    text-align: justify;
}
</style>"""

DOCX_EXPORT_IMAGE_CSS = """<style type="text/css">
.fr-element.fr-view table img,
.fr-view table img {
    width: 120px !important;
    height: 60px !important;
    max-width: 120px !important;
    max-height: 60px !important;
    display: block;
    margin: 0 auto;
}
</style>"""

DOCX_SIGNATURE_IMG_WIDTH_PX = 120
DOCX_SIGNATURE_IMG_HEIGHT_PX = 60
DOCX_SIGNATURE_IMG_STYLE = (
    f'width:{DOCX_SIGNATURE_IMG_WIDTH_PX}px;'
    f'height:{DOCX_SIGNATURE_IMG_HEIGHT_PX}px;'
    'display:block;margin:0 auto'
)


def build_docx_html_document(body_html: str) -> str:
    """Full HTML document for Word export (same table/justify CSS as PDF)."""
    doc_css = get_template('document_css_template.html').render()
    return (
        '<!DOCTYPE html>\n<html lang="fr">\n<head>\n'
        '<meta charset="UTF-8">\n'
        f'{doc_css}\n{DOCX_EXPORT_JUSTIFY_CSS}\n{DOCX_EXPORT_IMAGE_CSS}\n'
        '</head>\n<body>\n'
        f'<div class="fr-element fr-view">{body_html or ""}</div>\n'
        '</body>\n</html>'
    )


def _enhance_justify_for_docx(html: str) -> str:
    """Inline justify on Froala class blocks (CSS classes are lost in RTF)."""
    import re

    def _add_justify_style(match: re.Match) -> str:
        tag = match.group(1)
        attrs = match.group(2)
        if 'text-align' in attrs.lower():
            return match.group(0)
        return f'<{tag}{attrs} style="text-align:justify">'

    return re.sub(
        r'<(p|div)([^>]*class="[^"]*fr-text-justify[^"]*"[^>]*)>',
        _add_justify_style,
        html,
        flags=re.IGNORECASE,
    )


def _resize_data_uri_image(
    src: str, max_width: int, max_height: int
) -> str | None:
    """Downscale embedded signature so Word/Docs do not use the native pixel size."""
    import base64
    import io
    import re

    match = re.match(
        r'data:image/([^;]+);base64,(.+)', src, re.IGNORECASE | re.DOTALL
    )
    if not match:
        return None
    fmt = match.group(1).upper().replace('JPG', 'JPEG')
    if fmt not in {'PNG', 'JPEG', 'GIF', 'WEBP'}:
        fmt = 'PNG'
    try:
        from PIL import Image

        raw = base64.b64decode(match.group(2), validate=False)
        image = Image.open(io.BytesIO(raw))
        image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        save_fmt = 'PNG' if fmt == 'WEBP' else fmt
        image.save(buffer, format=save_fmt)
        encoded = base64.b64encode(buffer.getvalue()).decode('ascii')
        mime = save_fmt.lower()
        return f'data:image/{mime};base64,{encoded}'
    except Exception:
        logger.debug(
            'Could not resize embedded image for docx export', exc_info=True
        )
        return None


def _normalize_img_tag_for_docx(tag: str) -> str:
    """Rebuild ``img`` with fixed dimensions (Word ignores max-width/max-height)."""
    import re

    src_match = re.search(r'src\s*=\s*"([^"]*)"', tag, re.IGNORECASE)
    if not src_match:
        return tag
    src = src_match.group(1)
    if src.lower().startswith('data:image'):
        resized = _resize_data_uri_image(
            src,
            DOCX_SIGNATURE_IMG_WIDTH_PX,
            DOCX_SIGNATURE_IMG_HEIGHT_PX,
        )
        if resized:
            src = resized
    width = DOCX_SIGNATURE_IMG_WIDTH_PX
    height = DOCX_SIGNATURE_IMG_HEIGHT_PX
    return (
        f'<img src="{src}" width="{width}" height="{height}" '
        f'style="{DOCX_SIGNATURE_IMG_STYLE}" />'
    )


def _enhance_signature_images_for_docx(html: str) -> str:
    import re

    return re.sub(
        r'<img\b[^>]*>',
        lambda match: _normalize_img_tag_for_docx(match.group(0)),
        html,
        flags=re.IGNORECASE,
    )


def _enhance_tables_for_docx(html: str) -> str:
    """HTML border attributes help the Office File API preserve table grids."""
    import re

    return re.sub(
        r'<table(?![^>]*\bborder=)',
        '<table border="1" cellpadding="6" cellspacing="0" '
        'style="border-collapse:collapse;width:100%;table-layout:fixed"',
        html,
        flags=re.IGNORECASE,
    )


def _convert_html_to_docx_via_office_api(html: str) -> bytes | None:
    import requests

    base_url = getattr(
        settings,
        'OFFICE_FILE_API_URL',
        'http://office-file-api:8080',
    )
    try:
        rtf_response = requests.post(
            f'{base_url}/api/conversion/html-to-rtf',
            json={'htmlContent': html},
            timeout=60,
        )
        rtf_response.raise_for_status()
        docx_response = requests.post(
            f'{base_url}/api/conversion/rtf-to-docx',
            json={'rtfContent': rtf_response.text},
            timeout=60,
        )
        docx_response.raise_for_status()
        return docx_response.content
    except Exception:
        logger.warning(
            'Office File API html→rtf→docx failed, falling back to pandoc',
            exc_info=True,
        )
        return None


def _convert_html_to_docx_via_pandoc(html: str) -> bytes:
    import pypandoc

    with NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
        output_path = tmp.name
    try:
        pypandoc.convert_text(
            html,
            'docx',
            format='html',
            outputfile=output_path,
        )
        return Path(output_path).read_bytes()
    finally:
        Path(output_path).unlink(missing_ok=True)


def convert_html_to_docx_bytes(html: str) -> bytes:
    """Convert HTML to DOCX; prefers Office File API for table borders / justify."""
    html = _enhance_justify_for_docx(html)
    html = _enhance_signature_images_for_docx(html)
    html = _enhance_tables_for_docx(html)
    docx = _convert_html_to_docx_via_office_api(html)
    if docx is not None:
        return docx
    return _convert_html_to_docx_via_pandoc(html)
