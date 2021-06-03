default_app_config = "mighty.applications.nationality.apps.DocumentConfig"

from django.core.files import File
from django.template import Context, Template
from django.utils.text import get_valid_filename
from mighty.applications.document.apps import DocumentConfig as conf
import pdfkit, tempfile, os, shutil

fields = ("based_on", "config", "context")
fields_sign = fields + ("signatory", "is_signed")

def generate_pdf(**kwargs):
    filename = kwargs.get("file_name", False)
    header_enable, footer_enable = False, False
    options = kwargs.get("options", conf.pdf_options)
    conf_header = kwargs.get("conf_header", conf.pdf_header)
    conf_footer = kwargs.get("conf_footer", conf.pdf_footer)
    header = kwargs.get("header", False)
    footer = kwargs.get("footer", False)
    context = Context(kwargs.get("context", {}))
    content = kwargs.get("content", False)

    # header
    if header:
        header = conf.pdf_header % header
        header_html = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
        header_html.write(Template(header).render(context).encode("utf-8"))
        header_html.close()
        header = header_html
        options["--header-html"] = header_html.name
        header_enable = True

    if footer:
        footer = conf.pdf_footer % footer
        footer_html = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
        footer_html.write(Template(footer).render(context).encode("utf-8"))
        footer_html.close()
        footer = footer_html
        options["--footer-html"] = footer_html.name
        footer_enable = True

    if content and file_name:
        tmp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=True)
        content_html = Template(content).render(context)
        pdf = pdfkit.from_string(content_html, tmp_pdf.name, options=options)
        path_tmp = tmp_pdf.name
        valid_file_name = get_valid_filename(filename)
        path_convene = tempfile.gettempdir() + "/" + valid_file_name
        shutil.copyfile(path_tmp, path_convene)

        # a verifier
    os.remove(footer_html.name)
    os.remove(header_html.name)

def remove_tmpdf(files):
    for f in files:
        if hasattr(f, "close"):
            f.close()
        #os.remove(f.)