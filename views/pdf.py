import json
import os
import tempfile

import pdfkit
import pypandoc

from django.http import FileResponse, HttpResponse
from django.template import Context, Template
from django.template.loader import get_template
from mighty.apps import MightyConfig as conf
from mighty.functions import setting
from mighty.views.crud import DetailView


class PDFView(DetailView):
    cache_object = None
    tmp_files = []
    post_data = {}
    in_browser = False

    # Configurables
    pdf_name = 'file.pdf'
    options = conf.pdf_options.copy()
    header_tpl = conf.pdf_header
    footer_tpl = conf.pdf_footer
    content_html = conf.pdf_content
    config = {}

    def post(self, request, *args, **kwargs):
        self.post_data = json.loads(request.body.decode('utf-8'))
        return self.get(request, *args, **kwargs)

    def get_object(self):
        if not self.cache_object:
            self.cache_object = super().get_object()
        return self.cache_object

    def get_context_data(self, **kwargs):
        return Context({'obj': self.get_object()})

    def has_option(self, key):
        return self.request.GET.get(key, self.get_config().get(key, False))

    def get_config(self):
        return self.config

    def get_pdf_name(self):
        return self.pdf_name

    def build_html_file(self, html_content):
        tmp_file = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
        tmp_file.write(html_content.encode('utf-8'))
        tmp_file.close()
        self.tmp_files.append(tmp_file.name)
        return tmp_file.name

    def render_section(self, template_str, context):
        return Template(template_str).render(context)

    def build_header_html(self):
        if self.has_option('header_enable'):
            html = self.render_section(self.get_header(), self.get_context_data())
            return self.build_html_file(html)
        return ''

    def build_footer_html(self):
        if self.has_option('footer_enable'):
            html = self.render_section(self.get_footer(), self.get_context_data())
            return self.build_html_file(html)
        return ''

    def get_header(self):
        return ''  # à personnaliser si nécessaire

    def get_footer(self):
        return ''  # à personnaliser si nécessaire

    def get_template(self, context):
        template_name = self.get_template_names()
        template = get_template(template_name)
        return self.content_html % template.render(context)

    def prepare_options(self):
        if self.has_option('header_enable'):
            self.options['--header-html'] = self.build_header_html()
        if self.has_option('footer_enable'):
            self.options['--footer-html'] = self.build_footer_html()
        self.options['orientation'] = self.get_config().get('orientation', 'Portrait')
        return self.options

    def generate_pdf_file(self, html_content):
        tmp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        pdfkit.from_string(html_content, tmp_pdf.name, options=self.options)
        self.tmp_files.append(tmp_pdf.name)
        return tmp_pdf.name

    def clean_tmp(self):
        for path in self.tmp_files:
            if os.path.exists(path):
                os.remove(path)
        self.tmp_files.clear()

    def render_to_word(self, context):
        html_content = Template(self.post_data.get('raw_template')).render(context)
        tmp_docx = tempfile.NamedTemporaryFile(suffix='.docx', delete=False)
        output_path = tmp_docx.name
        tmp_docx.close()

        pypandoc.convert_text(html_content, 'docx', format='html', outputfile=output_path)

        with open(output_path, 'rb') as f:
            docx_data = f.read()

        os.remove(output_path)
        response = HttpResponse(
            docx_data,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        )
        response['Content-Disposition'] = f'attachment; filename="{self.get_pdf_name().replace(".pdf", ".docx")}"'
        return response

    def save_pdf(self):
        return self.generate_pdf_file(self.html_content)

    def render_to_response(self, context, **response_kwargs):
        self.prepare_options()
        self.html_content = self.get_template(context)

        # Sauvegarde PDF si demandé + génération unique du PDF
        if self.request.GET.get('save'):
            pdf_path = self.save_pdf()  # Modifie save_pdf pour qu'elle renvoie le chemin du fichier
        else:
            # Générer le PDF temporaire sans sauvegarder si pas de demande save
            pdf_path = self.generate_pdf_file(self.html_content)

        # Word export
        if self.post_data.get('action') == 'word':
            return self.render_to_word(context)

        # Si rendu en navigateur
        if self.in_browser:
            response = FileResponse(open(pdf_path, 'rb'), filename=self.get_pdf_name())
            self.clean_tmp()
            return response

        # Sinon renvoyer le PDF en téléchargement
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()

        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{self.get_pdf_name()}"'
        self.clean_tmp()
        return response