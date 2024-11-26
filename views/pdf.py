
import json
import os
import tempfile

import pdfkit
import pypandoc
from django.db.models import Q
from django.http import FileResponse, HttpResponse
from django.template import Context, Template
from django.template.loader import get_template

from mighty.apps import MightyConfig as conf
from mighty.functions import setting
from mighty.views.crud import DetailView


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
    config = {}
    post_data = {}

    def post(self, request, *args, **kwargs):
        self.post_data = json.loads(request.body.decode('utf-8'))
        return self.get(request, *args, **kwargs)

    def get_object(self):
        if not self.cache_object:
            self.cache_object = super().get_object()
        return self.cache_object

    def get_header(self):
        return ""

    def build_header_html(self):
        if not self.header_html:
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as header_html:
                header = self.get_header() if self.has_option("header_enable") else ""
                header_html.write(Template(header).render(self.get_context_data()).encode("utf-8"))
            self.header_html = header_html
        return self.header_html

    def get_footer(self):
        return ""

    def build_footer_html(self):
        if not self.footer_html:
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as footer_html:
                footer = self.get_footer() if self.has_option("footer_enable") else ""
                footer_html.write(Template(footer).render(self.get_context_data()).encode("utf-8"))
            self.footer_html = footer_html
        return self.footer_html

    def get_css_print(self):
        return os.path.join(setting('STATIC_ROOT', '/static'), 'css', 'print.css')

    def get_context_data(self, **kwargs):
        return Context({ "obj": self.get_object() })

    def get_config(self):
        return self.config

    def has_option(self, key):
        return self.request.GET.get(key, self.get_config().get(key, False))

    def prepare_options(self):
        self.options.update({
            '--header-html': self.build_header_html().name,
            '--footer-html': self.build_footer_html().name,
        })

        self.options.update({'orientation': self.get_config().get("orientation", 'Portrait') })
        return self.options

    def get_pdf_name(self):
        return self.pdf_name

    def get_tmp_pdf(self, context, config={}):
        self.config_override = config
        if not self.tmp_pdf:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
                pdfkit.from_string(self.get_template(context), tmp_pdf.name, options=self.options)
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

    def render_to_word(self, context):
        html_content = Template(self.post_data.get("raw_template")).render(context)
        # Créer un fichier temporaire pour stocker le fichier DOCX
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp_file:
            output_path = tmp_file.name
            # Utiliser pypandoc pour convertir le HTML en DOCX et écrire dans le fichier temporaire
            pypandoc.convert_text(html_content, 'docx', format='html', outputfile=output_path)
        # Ouvrir le fichier temporaire pour le lire
        with open(output_path, 'rb') as docx_file:
            # Lire le contenu du fichier DOCX
            docx_content = docx_file.read()
        # Supprimer le fichier temporaire après lecture
        os.remove(output_path)
        # Préparer la réponse HTTP avec le fichier DOCX
        response = HttpResponse(docx_content, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = 'attachment; filename="%s"' %  self.get_pdf_name().replace("pdf", "docx")
        return response

    def render_to_response(self, context, **response_kwargs):
        self.prepare_options()
        if self.request.GET.get('save', False):
            self.save_pdf(context)
        if self.post_data.get('action', False) == 'word':
            return self.render_to_word(context)
        if self.in_browser:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=True) as tmp_pdf:
                pdf = pdfkit.from_string(self.get_template(context), tmp_pdf.name, options=self.options)
                self.clean_tmp()
                return FileResponse(open(tmp_pdf.name, 'rb'), filename=self.get_pdf_name())
        pdf = pdfkit.from_string(self.get_template(context), False, options=self.options)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % self.get_pdf_name()
        self.clean_tmp()
        return response
