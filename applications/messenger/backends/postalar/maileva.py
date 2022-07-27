from django.core.files import File

from mighty.applications.messenger.backends import MissiveBackend
from mighty.apps import MightyConfig
from mighty.functions import setting

from uuid import uuid4
import os, requests, json

from mighty.functions import get_logger
logger = get_logger()

class MissiveBackend(MissiveBackend):
    api_sandbox = {
        "webhook": "https://api.sandbox.maileva.net/notification_center/v2/subscriptions",
        "auth": "https://connexion.sandbox.maileva.net/auth/realms/services/protocol/openid-connect/token",
        "sendings": "https://api.sandbox.maileva.net/registered_mail/v2/sendings",
        "documents": "https://api.sandbox.maileva.net/registered_mail/v2/sendings/%s/documents",
        "recipients": "https://api.sandbox.maileva.net/registered_mail/v2/sendings/%s/recipients",
        "submit": "https://api.sandbox.maileva.net/registered_mail/v2/sendings/%s/submit",
    }
    api_official = {
        "webhook": "https://api.maileva.com/notification_center/v2/subscriptions",
        "auth": "https://connexion.maileva.com/auth/realms/services/protocol/openid-connect/token",
        "sendings": "https://api.maileva.com/registered_mail/v2/sendings",
        "documents": "https://api.maileva.com/registered_mail/v2/sendings/%s/documents",
        "recipients": "https://api.maileva.com/registered_mail/v2/sendings/%s/recipients",
        "submit": "https://api.maileva.com/registered_mail/v2/sendings/%s/submit",
    }
    webhook_status = [
        "ON_STATUS_ACCEPTED",
        "ON_STATUS_REJECTED",
        "ON_STATUS_PROCESSED",
        "ON_DEPOSIT_PROOF_RECEIVED",
    ]
    sending_id = None
    access_token = None
    priority = 1
    in_error = False
    fields = ["denomination", "fullname", "complement", "address"]

    @property
    def auth_data(self):
        return {
            "username": setting("MAILEVA_USERNAME"),
            "password": setting("MAILEVA_PASSWORD"),
            "grant_type": "password",
            "client_id": setting("MAILEVA_CLIENTID"),
            "client_secret": setting("MAILEVA_SECRET"),
        }

    @property
    def our_data(self):
        return {
            "name": self.missive.subject,
            "custom_id": self.missive.msg_id,
            "custom_data": self.missive.msg_id,
            "acknowledgement_of_receipt": True,
            "acknowledgement_of_receipt_scanning": False,
            "color_printing": True,
            "duplex_printing": True,
            "optional_address_sheet": False,
            "notification_email": setting("MAILEVA_NOTIFICATION"),
            "archiving_duration": 3,
            "sender_address_line_1": setting("MAILEVA_SENDER1"),
            "sender_address_line_2": setting("MAILEVA_SENDER2"),
            "sender_address_line_3": setting("MAILEVA_SENDER3"),
            "sender_address_line_4": setting("MAILEVA_SENDER4"),
            "sender_address_line_5": setting("MAILEVA_SENDER5"),
            "sender_address_line_6": setting("MAILEVA_SENDER6"),
            "sender_country_code": setting("MAILEVA_SENDERC"),
            #"envelope_windows_type": "SIMPLE",
            #"postage_type": "ECONOMIC",
            #"return_envelope": None
        }

    @property
    def webhook_data(self):
        return {
            "event_type": "ON_STATUS_ACCEPTED",
            "resource_type": "mail/v2/sendings",
            "callback_url": "https://api.mycompany.com/callback",
        }

    @property
    def target_data(self):
        data = {
            "custom_id":  self.missive.msg_id,
            "custom_data": self.missive.msg_id,
            "address_line_6": self.missive.city,
            "country_code": self.missive.country_code.upper(),
        }
        for i, field in enumerate(self.fields):
            attr = getattr(self.missive, field)
            if attr:
                data["address_line_"+str(i)] = attr
        return data

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

    def postal_attachments(self):
        if self.missive.attachments:
            api = self.api_url["documents"] % self.sending_id
            headers = self.api_headers
            logs = []
            for document in self.missive.attachments:
                self.priority+=1
                doc_name = os.path.basename(document.name)
                logs.append(doc_name)
                files = {'document': (doc_name, open(document.name, 'rb'))}
                data = {'metadata': json.dumps({"priority": self.priority, "name": doc_name})}
                response = requests.post(api, headers=headers, files=files, data=data)
                self.valid_response(response)
            self.missive.logs['attachments'] = logs
        return False if self.in_error else True

    def add_recipients(self):
        api = self.api_url["recipients"] % self.sending_id
        response = requests.post(api, headers=self.api_headers, json=self.target_data)
        return self.valid_response(response)

    def submit(self):
        api = self.api_url["submit"] % self.sending_id
        response = requests.post(api, headers=self.api_headers)
        return self.valid_response(response)

    def enable_webhooks(self):
        for status in self.webhook_status:
            api = self.api_url["webhook"]
            response = requests.post(api, headers=self.api_headers)
            return self.valid_response(response)

    def check_postalar(self):
        self.authentication()
        url = self.api_url["sendings"] + "/" + self.missive.partner_id
        response = requests.get(url, headers=self.api_headers)
        return response.json()

    def send_postal(self):
        self.missive.msg_id = str(uuid4())
        self.authentication()
        if not self.in_error:
            self.create_sending()
        if not self.in_error:
            self.add_recipients()
        if not self.in_error:
            self.postal_base()
            self.postal_attachments()
            os.remove(self.path_base_doc)
        if not self.in_error and self.submit():
            self.missive.to_sent()
            #self.enable_webhooks()
        else:
            self.missive.to_error()
        self.missive.save()
        return self.missive.status
