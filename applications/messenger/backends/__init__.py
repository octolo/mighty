import os
import pathlib
import tempfile

import pdfkit
from django.core.mail import EmailMessage
from django.core.mail.message import make_msgid
from django.template import Context, Template

from mighty.applications.logger import EnableLogger
from mighty.applications.messenger import choices
from mighty.applications.messenger.apps import MessengerConfig as conf  # noqa
from mighty.apps import MightyConfig as MightyConfig
from mighty.functions import setting
from mighty.models import Missive  # noqa


class MissiveBackend(EnableLogger):
    in_error = False
    email = None
    sms = None
    postal = None
    path_base_doc = None
    js_admin = True
    has_proofs = False

    def __init__(self, missive, *args, **kwargs):
        self.missive = missive

    @property
    def extra(self):
        return {'user': self.missive.content_object, 'app': 'messenger'}

    @property
    def message(self):
        return self.missive.txt or self.missive.html

    def send(self):
        return getattr(self, f'send_{self.missive.mode.lower()}')()

    def send_sms(self):
        over_target = setting('MISSIVE_PHONE', False)
        self.missive.target = over_target or self.missive.target
        self.logger.info(
            f'SMS - from : {self.sender_sms}, to : {self.missive.target}'
        )
        if setting('MISSIVE_SERVICE', False):
            pass
        self.missive.status = choices.STATUS_SENT
        self.missive.save()
        self.logger.info(f'send sms: {self.message}', extra=self.extra)
        return self.missive.status

    def email_attachments(self):
        if self.missive.attachments:
            logs = []
            for document in self.missive.attachments:
                if setting('MISSIVE_SERVICE', False):
                    self.email.attach(
                        os.path.basename(document.name),
                        document.read(),
                        'application/pdf',
                    )
                logs.append(os.path.basename(document.name))
            self.missive.logs['attachments'] = logs
        if setting('MISSIVE_SERVICE', False):
            self.email.send()

    @property
    def sender_email(self):
        if self.missive.name:
            return f'{self.missive.name} <{self.missive.sender}>'
        return self.missive.sender

    @property
    def reply_email(self):
        return self.missive.reply or self.missive.sender

    @property
    def reply_name(self):
        return self.missive.reply_name or self.missive.name

    def send_email(self):
        over_target = setting('MISSIVE_EMAIL', False)
        self.missive.target = over_target or self.missive.target
        self.logger.info(
            f'Email - from : {self.sender_email}, to : {self.missive.target}, reply : {self.reply_email}'
        )
        if setting('MISSIVE_SERVICE', False):
            self.missive.msg_id = make_msgid()
            self.email = EmailMessage(
                self.missive.subject,
                self.missive.html_format or str(self.missive.txt),
                self.sender_email,
                [self.missive.target],
                reply_to=[self.reply_email],
                headers={'Message-Id': self.missive.msg_id},
            )
            if self.missive.html_format:
                self.email.content_subtype = 'html'
        self.email_attachments()
        self.missive.to_sent()
        self.missive.save()
        return self.missive.status

    def send_emailar(self):
        return self.send_email()

    def add_log_array(self, key, log):
        if self.missive.logs.get(key):
            self.missive.logs[key].append(log)
        else:
            self.missive.logs[key] = [log]

    def postal_add_attachment(self, attachment):
        self.add_log_array('attachments', attachment.name)

    def postal_attachments(self):
        if self.missive.attachments:
            for document in self.missive.attachments:
                self.postal_add_attachment(document)

    def postal_template(self, context):
        return Template(self.missive.html or '').render(context)

    def generate_postal_firstpage(self):
        """Generate the postal first-page PDF and return its filesystem path.

        Caller is responsible for deleting the returned file.
        """
        context = Context()

        header_html = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
        header_html.write(
            Template(self.missive.header_html or '')
            .render(context)
            .encode('utf-8')
        )
        header_html.close()

        footer_html = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
        footer_html.write(
            Template(self.missive.footer_html or '')
            .render(context)
            .encode('utf-8')
        )
        footer_html.close()

        tmp_pdf = tempfile.NamedTemporaryFile(
            suffix='postalfirstpage.pdf', delete=False
        )
        tmp_pdf.close()
        try:
            pdfkit.from_string(
                self.postal_template(context),
                tmp_pdf.name,
                options={
                    'encoding': 'UTF-8',
                    '--header-html': header_html.name,
                    '--footer-html': footer_html.name,
                    'page-size': 'A4',
                    'margin-top': '0.75in',
                    'margin-right': '0.75in',
                    'margin-bottom': '0.75in',
                    'margin-left': '0.75in',
                    'custom-header': [('Accept-Encoding', 'gzip')],
                },
            )
            # Rewrite pages: sandbox WAF often blocks raw wkhtmltopdf output.
            try:
                from io import BytesIO

                from pypdf import PdfReader, PdfWriter

                with open(tmp_pdf.name, 'rb') as handle:
                    raw = handle.read()
                reader = PdfReader(BytesIO(raw))
                writer = PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)
                with open(tmp_pdf.name, 'wb') as handle:
                    writer.write(handle)
            except Exception:
                pass
        finally:
            pathlib.Path(header_html.name).unlink(missing_ok=True)
            pathlib.Path(footer_html.name).unlink(missing_ok=True)
        return tmp_pdf.name

    def download_postal_firstpage(self):
        """Generate the first-page PDF and return it as a download response."""
        from io import BytesIO

        from django.http import FileResponse

        path = self.generate_postal_firstpage()
        try:
            with open(path, 'rb') as handle:
                content = handle.read()
        finally:
            pathlib.Path(path).unlink(missing_ok=True)
        filename = f'postalfirstpage_{self.missive.pk}.pdf'
        return FileResponse(
            BytesIO(content), as_attachment=True, filename=filename
        )

    def postal_base(self):
        path = self.generate_postal_firstpage()
        try:
            with open(path, 'rb') as handle:
                self.postal_add_attachment(handle)
        finally:
            pathlib.Path(path).unlink(missing_ok=True)

    def send_postal(self):
        self.postal_base()
        self.postal_attachments()
        if self.path_base_doc:
            pathlib.Path(self.path_base_doc).unlink(missing_ok=True)
        self.missive.to_sent()
        self.missive.save()
        return self.missive.status

    def check_documents(self):
        return '{}'

    def send_postalar(self):
        return self.send_postal()

    def send_web(self):
        return NotImplementedError('Web mode not implemented')

    def send_app(self):
        raise NotImplementedError('App mode not implemented')

    def check(self, missive):
        return NotImplementedError('Check mode not implemented')

    def on_webhook(self, request):
        return NotImplementedError('Webhook mode not implemented')

    def cancel(self):
        return NotImplementedError('Cancel mode not implemented')

    def get_prooflist(self):
        if self.has_proofs:
            return NotImplementedError('Get proof mode not implemented')
        return []

    def get_proof(self, **kwargs):
        if self.has_proofs:
            return NotImplementedError('Get proof mode not implemented')
        return None

    def download_proof(self, http_response=False, **kwargs):
        return NotImplementedError('Download proof mode not implemented')

    def get_class(self):
        return NotImplementedError('Get class mode not implemented')

    def get_type(self):
        return NotImplementedError('Get type mode not implemented')

    def get_reference(self):
        return NotImplementedError('Get reference mode not implemented')

    def get_price(self):
        return NotImplementedError('Get price mode not implemented')

    def get_invoice(self):
        return []

    def get_billed_page(self):
        return NotImplementedError('Get billed page mode not implemented')

    def get_external_reference(self):
        return NotImplementedError('Get reference mode not implemented')

    def get_external_status(self):
        return NotImplementedError('Get status mode not implemented')

    def get_color(self):
        return NotImplementedError('Get color mode not implemented')

    def get_price_infos(self):
        return {}
