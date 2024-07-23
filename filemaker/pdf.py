from django.conf import settings
from django.contrib.staticfiles.finders import find as find_static_file
from django.template import Template, Context
from django.core.files.base import ContentFile
from weasyprint import HTML
import logger
logging = logger.get_logger(__name__)

class FileMakerPDF:
    str_options = ["html", "header", "footer", "lang", "title", "charset"]
    arr_options = ["css",]
    dct_options = ["config", "context", "fonts", "images"]

    lang, title, charset = "en", "Document", "UTF-8"
    header, html, footer = "", "", ""
    config, context, fonts, images = {}, {}, {}, {}
    current_pdf = None

    body_html = """<!DOCTYPE html>
<html>
    <head lang="%(lang)s">
        <meta charset="%(charset)s">
        <title>%(title)s</title>
        <style>%(style)s</style>
        %(head)s
    </head>
    <body class="ck-content">%(body)s</body>
    <footer>%(footer)s</footer>
</html>"""

    # Init options
    def init_options(self, **kwargs):
        logging.warning(self.css)
        self.css = settings.CSS_FILES_WEASYPRINT or []
        for key,value in kwargs.items():
            if key in self.str_options:
                setattr(self, key, value)
            elif key in self.arr_options:
                for val in value:
                    if val not in getattr(self, key):
                        getattr(self, key).append(val)
            elif key in self.dct_options:
                getattr(self, key).update(value)

    def __init__(self, **kwargs):
        self.init_options(**settings.PDFMAKER)
        self.init_options(**kwargs)
        logging.warning(self.css)


    # Font rules
    def get_font_rule(self, font, name):
        return "\n".join([
            "@font-face {",
            "    font-family: '%s';" % name,
            "    src: url(file://%s);" % find_static_file("fonts/%s" % font),
            "}",
        ])

    def get_style_font_face(self):
        return "\n".join([self.get_font_rule(font, name)
            for font, name in self.fonts.items()])

    # CSS rules
    def get_style(self):
        style = ""
        style += "\n".join([
            "@import url('file://%s');" % find_static_file(css)
            for css in self.css
        ])
        style += self.get_style_font_face()
        return style

    # HTML parts
    def get_header_html(self):
        return self.header

    def get_body_html(self):
        template = Template(self.html)
        return template.render(Context(self.context))

    def get_footer_html(self):
        return self.footer

    def get_html_string(self):
        return self.body_html % {
            "title": self.title,
            "lang": self.lang,
            "charset": self.charset,
            "style": self.get_style(),
            "head": self.get_header_html(),
            "body": self.get_body_html(),
            "footer": self.get_footer_html(),
        }

    def write_html(self, **kwargs):
        self.init_options(**kwargs)
        return HTML(string=kwargs.get("html", self.get_html_string()))

    def write_pdf(self, **kwargs):
        self.init_options(**kwargs)
        self.current_pdf = self.write_html(html=self.get_html_string()).write_pdf(kwargs.get(buffer))
        return self.current_pdf

    def as_content_file(self, filename):
        return ContentFile(self.current_pdf, filename)
