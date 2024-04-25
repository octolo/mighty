from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.utils.text import get_valid_filename
from django.contrib.auth import get_user_model
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.core.mail.message import make_msgid
from django.template import Context, Template

from mighty.apps import MightyConfig
from mighty.functions import setting, searchable
from mighty.models import Missive
from mighty.applications.messenger import choices
from mighty.applications.messenger.apps import MessengerConfig as conf
import datetime, logging, os, tempfile, pdfkit, shutil

logger = logging.getLogger(__name__)
from mighty.applications.logger import EnableLogger

class MissiveBackend(EnableLogger):
    in_error = False
    email = None
    sms = None
    postal = None
    path_base_doc = None
    js_admin = True

    def __init__(self, missive, *args, **kwargs):
        self.missive = missive

    @property
    def extra(self):
        return {'user': self.missive.content_object, 'app': 'messenger'}

    @property
    def message(self):
        return self.missive.txt if self.missive.txt else self.missive.html

    def send(self):
        return getattr(self, 'send_%s' % self.missive.mode.lower())()

    def send_sms(self):
        over_target = setting('MISSIVE_PHONE', False)
        self.missive.target = over_target if over_target else self.missive.target
        self.logger.info("SMS - from : %s, to : %s" %
            (self.sender_sms, self.missive.target))
        if setting('MISSIVE_SERVICE', False):
            pass
        self.missive.status = choices.STATUS_SENT
        self.missive.save()
        logger.info("send sms: %s" % self.message, extra=self.extra)
        return self.missive.status

    def email_attachments(self):
        if self.missive.attachments:
            logs = []
            for document in self.missive.attachments:
                if setting('MISSIVE_SERVICE', False):
                    self.email.attach(os.path.basename(document.name), document.read(), 'application/pdf')
                logs.append(os.path.basename(document.name))
            self.missive.logs['attachments'] = logs
        if setting('MISSIVE_SERVICE', False):
            self.email.send()

    @property
    def sender_email(self):
        if self.missive.name:
            return "%s <%s>" % (self.missive.name, self.missive.sender)
        return self.missive.sender

    @property
    def reply_email(self):
        return self.missive.reply if self.missive.reply else self.missive.sender

    @property
    def reply_name(self):
        return self.missive.reply_name if self.missive.reply_name else self.missive.name


    def send_email(self):
        over_target = setting('MISSIVE_EMAIL', False)
        self.missive.target = over_target if over_target else self.missive.target
        self.logger.info("Email - from : %s, to : %s, reply : %s" %
            (self.sender_email, self.missive.target, self.reply_email))
        if setting('MISSIVE_SERVICE', False):
            self.missive.msg_id = make_msgid()
            self.email = EmailMessage(
                self.missive.subject,
                self.missive.html_format if self.missive.html_format else str(self.missive.txt),
                self.sender_email,
                [self.missive.target],
                reply_to=[self.reply_email],
                headers={'Message-Id': self.missive.msg_id}
            )
            if self.missive.html_format:
                self.email.content_subtype = "html"
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
        logs.append(os.path.basename(attachment.name))
        self.add_log_array('attachments', attachment.name)

    def postal_attachments(self):
        if self.missive.attachments:
            logs = []
            for document in self.missive.attachments:
                self.postal_add_attachment(document)

    def postal_template(self, context):
        return Template(self.missive.html).render(context)

    def postal_base(self):
        options = MightyConfig.pdf_options
        context = Context()

        # header
        header = self.missive.header_html
        header_html = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
        header_html.write(Template(header).render(context).encode("utf-8"))
        header_html.close()

        # footer
        footer = self.missive.footer_html
        footer_html = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
        footer_html.write(Template(footer).render(context).encode("utf-8"))
        footer_html.close()


        # first file
        with tempfile.NamedTemporaryFile(suffix='postalfirstpage.pdf', delete=False) as tmp_pdf:
            #tmp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=True)
            content_html = self.postal_template(context)
            pdf = pdfkit.from_string(content_html, tmp_pdf.name, options={
                'encoding': "UTF-8",
                '--header-html': header_html.name,
                '--footer-html': footer_html.name,
                'page-size':'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'custom-header' : [
                    ('Accept-Encoding', 'gzip')
                ]
            })
            self.postal_add_attachment(tmp_pdf)
        #path_tmp = tmp_pdf.name
        #doc_name = os.path.basename(path_tmp)
        #self.path_base_doc = path_tmp
        #valid_file_name = searchable(get_valid_filename('%s.pdf' % self.missive.subject))
        #path_basedoc = tempfile.gettempdir() + '/' + valid_file_name
        #shutil.copyfile(path_tmp, path_basedoc)
        #self.missive.attachments.insert(0, open(path_tmp, 'rb'))
        os.remove(footer_html.name)
        os.remove(header_html.name)
        #if self.missive.status != choices.STATUS_FILETEST:
        #    tmp_pdf.close()
        #os.remove(path_basedoc)
        #return self.valid_response(response)

    def send_postal(self):
        self.postal_base()
        self.postal_attachments()
        os.remove(self.path_base_doc)
        self.missive.to_sent()
        self.missive.save()
        return self.missive.status

    def check_documents(self):
        return "{}"

    def send_postalar(self):
        return self.send_postal()

    def send_web(self):
        return ""

    def send_app(self):
        return ""

    def check(self, missive):
        return True

    def on_webhook(self, request):
        return {}
