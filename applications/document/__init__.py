default_app_config = "mighty.applications.nationality.apps.DocumentConfig"

from django.conf import settings
from django.core.files import File
from django.template import Context, Template
from django.utils.text import get_valid_filename
from django.template.loader import get_template
from mighty.applications.document.apps import DocumentConfig as conf
import pdfkit, tempfile, os, shutil

fields = ("based_on", "config", "context")
fields_sign = fields + ("signatory", "is_signed")

def generate_pdf(**kwargs):
    header_enable, footer_enable = False, False
    file_name = kwargs.get("file_name", False)
    options = kwargs.get("options", conf.pdf_options)
    conf_header = kwargs.get("conf_header", conf.pdf_header)
    conf_footer = kwargs.get("conf_footer", conf.pdf_footer)
    header = kwargs.get("header", False)
    footer = kwargs.get("footer", False)
    context = kwargs.get("context", {})
    content = kwargs.get("content", False)
    content_html = kwargs.get("content_html", False)
    as_string = kwargs.get("as_string", False)
    context.update({
        "media": os.path.abspath(settings.MEDIA_ROOT),
        "static": os.path.abspath(settings.MEDIA_ROOT),
    })

    # header
    if header:
        header = conf.pdf_header % header
        header_html = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
        header_html.write(Template(header).render(Context(context)).encode("utf-8"))
        header_html.close()
        header = header_html
        options["--header-html"] = header_html.name
        header_enable = True

    if footer:
        footer = conf.pdf_footer % footer
        footer_html = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
        footer_html.write(Template(footer).render(Context(context)).encode("utf-8"))
        footer_html.close()
        footer = footer_html
        options["--footer-html"] = footer_html.name
        footer_enable = True

    if (content or content_html) and file_name:
        tmp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=True)
        if content_html:
            content_html = Template(content_html).render(Context(context))
        else:
            content_html = get_template(content).render(context)
        pdf = pdfkit.from_string(content_html, tmp_pdf.name, options=options)
        path_tmp = tmp_pdf.name
        valid_file_name = get_valid_filename(file_name)
        final_pdf = tempfile.gettempdir() + "/" + valid_file_name
        shutil.copyfile(path_tmp, final_pdf)

    # a verifier
    if footer:
        os.remove(footer_html.name)
    if header:
        os.remove(header_html.name)
    if as_string:
        tmp_pdf.close()
        os.remove(final_pdf)
        return content_html
    return final_pdf, tmp_pdf

#def remove_tmpdf(files):
#    for f in files:
#        if hasattr(f, "close"):
#            f.close()
#        #os.remove(f.)