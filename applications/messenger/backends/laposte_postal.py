from django.core.files import File
from django.utils.text import get_valid_filename
from django.template import Context, Template

from mighty.applications.messenger.backends import MissiveBackend
from mighty.apps import MightyConfig
from mighty.functions import setting

from uuid import uuid4
import tempfile, os, requests, pdfkit, shutil, json

from mighty.functions import get_logger
logger = get_logger()

class MissiveBackend(MissiveBackend):
    api_sandbox = {
        "auth": "https://api.sandbox.maileva.net/authentication/oauth2/token",
        "sendings": "https://api.sandbox.maileva.net/mail/v2/sendings",
        "documents": "https://api.sandbox.maileva.net/mail/v2/sendings/%s/documents",
        "recipients": "https://api.sandbox.maileva.net/mail/v2/sendings/%s/recipients",
        "submit": "https://api.sandbox.maileva.net/mail/v2/sendings/%s/submit",
    }
    api_official = {
        "auth": "https://connexion.maileva.com/auth/realms/services/protocol/openid-connect/token",
        "sendings": "https://api.maileva.com/mail/v2/sendings",
        "documents": "https://api.maileva.com/mail/v2/sendings/%s/documents",
        "recipients": "https://api.maileva.com/mail/v2/sendings/%s/recipients",
        "submit": "https://api.maileva.com/mail/v2/sendings/%s/submit",
    }
    sending_id = None
    access_token = None
    priority = 1
    in_error = False

    @property
    def auth_data(self):
        return {
            "username": setting("LAPOSTE_USERNAME"),
            "password": setting("LAPOSTE_PASSWORD"),
            "grant_type": "password",
            "client_id": setting("LAPOSTE_CLIENTID"),
            "client_secret": setting("LAPOSTE_SECRET"),
        }

    @property
    def our_data(self):
        return {
            "name": self.missive.subject,
            "custom_id": self.missive.msg_id,
            "custom_data": self.missive.msg_id,
            "color_printing": True,
            "duplex_printing": True,
            "optional_address_sheet": False,
            "notification_email": "postal@octolo.tech",
            "archiving_duration": 0,
            "envelope_windows_type": "SIMPLE",
            "postage_type": "ECONOMIC",
        }

    @property
    def target_data(self):
        return {
            "custom_id":  self.missive.msg_id,
            "custom_data": self.missive.msg_id,
            "address_line_1": self.missive.denomination,
            "address_line_2": self.missive.target,
            "address_line_3": self.missive.complement,
            "address_line_4": self.missive.address,
            "address_line_5": "",
            "address_line_6": self.missive.city,
            "country_code": self.missive.country_code.upper(),
        }

    @property
    def api_url(self):
        if setting('MISSIVE_SERVICE', False):
            return self.api_sandbox
        return self.api_sandbox

    @property
    def api_headers(self):
        return {
            'accept': 'application/json',
            'Authorization': 'Bearer '+self.access_token,
        }

    def valid_response(self, response):
        if response.status_code not in [200, 201]:
            self.missive.trace = str(response.json())
            if response.status_code in [401, 404]:
                self.missive.code_error = response.json()["code"]
            self.in_error = True
            return False
        return True
            

    def authentication(self):
        response = requests.post(self.api_url["auth"], data=self.auth_data)
        self.access_token = response.json()["access_token"]
        return self.valid_response(response)

    def create_sending(self):
        response = requests.post(self.api_url["sendings"], headers=self.api_headers, json=self.our_data)
        self.sending_id = response.json()["id"]
        self.missive.partner_id = self.sending_id
        return self.valid_response(response)

    def base_doc(self):
        api = self.api_url["documents"] % self.sending_id
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

        # file
        tmp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=True)
        content_html = Template(self.missive.html).render(context)
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
        path_tmp = tmp_pdf.name
        valid_file_name = get_valid_filename('%s.pdf' % self.missive.subject)
        path_basedoc = tempfile.gettempdir() + '/' + valid_file_name
        shutil.copyfile(path_tmp, path_basedoc)
        doc_name = os.path.basename(path_basedoc)
        headers = self.api_headers

        files = {'document': (doc_name, open(path_basedoc, 'rb'))}
        data = {'metadata': json.dumps({"priority": self.priority, "name": doc_name})}
        response = requests.post(api, headers=headers, files=files, data=data)

        os.remove(footer_html.name)
        os.remove(header_html.name)
        tmp_pdf.close()
        os.remove(path_basedoc)
        return self.valid_response(response)

    def add_documents(self):
        if self.missive.attachments:
            api = self.api_url["documents"] % self.sending_id
            logs = []
            for document in self.missive.attachments:
                self.priority+=1
                doc_name = os.path.basename(document.name)
                logs.append(doc_name)
                files = {'document': (doc_name, open(document.name, 'rb'))}
                data = {'metadata': json.dumps({"priority": self.priority, "name": doc_name})}
                response = requests.post(api, headers=headers, files=files, data=data)
                self.valid_response(response)
            self.missive.logs = logs
        return False if self.in_error else True

    def add_recipients(self):
        api = self.api_url["recipients"] % self.sending_id
        response = requests.post(api, headers=self.api_headers, json=self.target_data)
        return self.valid_response(response)

    def submit(self):
        api = self.api_url["submit"] % self.sending_id
        response = requests.post(api, headers=self.api_headers)
        return self.valid_response(response)

    def send_postal(self):
        self.missive.msg_id = str(uuid4())
        self.authentication()
        if not self.in_error:
            self.create_sending()
        if not self.in_error:
            self.add_recipients()
        if not self.in_error:
            self.base_doc()
        if not self.in_error:
            self.add_documents()
        if not self.in_error and self.submit():
            self.missive.to_sent()
        else:
            self.missive.to_error()
        self.missive.save()
        return self.missive.status

