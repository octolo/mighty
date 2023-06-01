from django.apps import AppConfig
from mighty import over_config
from mighty.functions import setting

class Config:
    pdf_options = {
        'encoding': 'UTF-8',
        'page-size':'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'custom-header' : [
            ('Accept-Encoding', 'gzip')
        ]
    }

    @property
    def pdf_header(self):
        from django.template.loader import get_template
        return get_template("document_header_template.html").render()
    @property
    def pdf_footer(self):
        from django.template.loader import get_template
        return get_template("document_footer_template.html").render()
    @property
    def pdf_content(self):
        from django.template.loader import get_template
        return get_template("document_content_template.html").render()

over_config(Config, setting('DOCUMENT'))
class DocumentConfig(AppConfig, Config):
    name = 'mighty.applications.document'
