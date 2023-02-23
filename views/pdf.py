
from django.http import HttpResponse, FileResponse
from django.template.loader import get_template
from django.template import Context, Template
from django.db.models import Q

from mighty.views.crud import DetailView
from mighty.apps import MightyConfig as conf
from mighty.functions import setting

import pdfkit, os, tempfile

class PDFView(DetailView):
    header_html = None
    footer_html = None
    cache_object = None
    in_browser = False
    pdf_name = 'file.pdf'
    options = conf.pdf_options
    header_tpl = conf.pdf_header
    footer_tpl = conf.pdf_footer
    content_html = conf.pdf_content
    tmp_pdf = None
    config_override = {}

    def get_object(self):
        if not self.cache_object:
            self.cache_object = super().get_object()
        return self.cache_object

    def get_header(self):
        return ""

    def build_header_html(self):
        if not self.header_html:
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as header_html:
                header = self.get_header()
                header_html.write(Template(header).render(self.get_context_data()).encode("utf-8"))
            self.header_html = header_html
        return self.header_html

    def get_footer(self):
        return ""

    def build_footer_html(self):
        if not self.footer_html:
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as footer_html:
                footer = self.get_footer()
                footer_html.write(Template(footer).render(self.get_context_data()).encode("utf-8"))
            self.footer_html = footer_html
        return self.footer_html

    def get_css_print(self):
        return os.path.join(setting('STATIC_ROOT', '/static'), 'css', 'print.css')

    def get_context_data(self, **kwargs):
        return Context({ "obj": self.get_object() })

    def get_options(self):
        print(self.config_override)
        if self.config_override.get("header_enable", False):
            self.options.update({
                '--header-html': self.build_header_html().name,
            })
        if self.config_override.get("footer_enable", False):
            self.options.update({
                '--footer-html': self.build_footer_html().name,
            })
        print(self.options)
        return self.options

    def get_pdf_name(self):
        return self.pdf_name

    def get_tmp_pdf(self, context, config={}):
        self.config_override = config
        if not self.tmp_pdf:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
                pdfkit.from_string(self.get_template(context), tmp_pdf.name, options=self.get_options())
                self.tmp_pdf = tmp_pdf
        return self.tmp_pdf

    def save_pdf(self, context):
        tmp_pdf = self.get_tmp_pdf(context)

    def get_template(self, context):
        template_name = self.get_template_names()
        template = get_template(template_name)
        return self.content_html % template.render(context)

    def clean_tmp(self):
        if self.header_html and os.path.isfile(self.header_html.name):
            os.remove(self.header_html.name)
        if self.footer_html and os.path.isfile(self.footer_html.name):
            os.remove(self.footer_html.name)
        if self.tmp_pdf and os.path.isfile(self.tmp_pdf.name):
            os.remove(self.tmp_pdf.name)

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('save', False): self.save_pdf(context)
        if self.in_browser:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=True) as tmp_pdf:
                pdf = pdfkit.from_string(self.get_template(context), tmp_pdf.name, options=self.get_options())
                self.clean_tmp()
                return FileResponse(open(tmp_pdf.name, 'rb'), filename=self.get_pdf_name())
        pdf = pdfkit.from_string(self.get_template(context), False, options=self.get_options())
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % self.get_pdf_name()
        self.clean_tmp()
        return response