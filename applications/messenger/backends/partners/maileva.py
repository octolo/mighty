from django.core.files import File
from django.shortcuts import get_object_or_404
from django.template import Template
from mighty.applications.messenger.backends import MissiveBackend
from mighty.applications.messenger import choices as _c
from mighty.apps import MightyConfig
from mighty.functions import setting
from mighty.models import Missive

from uuid import uuid4
import os, requests, json

from mighty.functions import get_logger
logger = get_logger()

class Maileva(MissiveBackend):
    status_ref = {
        "PENDING": _c.STATUS_PENDING,
        "ACCEPTED": _c.STATUS_ACCEPTED,
        "PROCESSED": _c.STATUS_PROCESSED,
        "DRAFT": _c.STATUS_ERROR,
        "REJECTED": _c.STATUS_REJECTED,
        "PROCESSED_WITH_ERRORS": _c.STATUS_PROCESSED,
    }
    events = [
        "ON_STATUS_ACCEPTED",
        "ON_STATUS_REJECTED",
        "ON_STATUS_PROCESSED",
        "ON_DEPOSIT_PROOF_RECEIVED",
    ]
    fields = ["denomination", "fullname", "complement", "address"]
    user_cache = None
    sending_id = None
    access_token = None
    priority = 1
    header_offset = 72

    @property
    def sender_height(self):
        return 145-self.header_offset

    @property
    def address_block(self):
        sender_style = "height:%spx;" % (str(self.sender_height))
        target_style = "height:171px;padding-bottom:35px;"
        sender_content = ""
        target_content = ""
        if self.missive.status == _c.STATUS_FILETEST:
            sender_style += "background-color:gray;color: white;"
            target_style += "background-color:blue;color: white;"
            sender_content = "SENDER"
            target_content = "TARGET"
        return """<div style="%s">%s</div><div style="%s">%s</div>""" % (sender_style, sender_content, target_style, target_content)

    def postal_template(self, context):
        return Template(self.address_block+self.missive.html).render(context)

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
    def postal_data(self):
        base = {
            "name": self.missive.subject,
            "custom_id": self.missive.msg_id,
            "custom_data": self.missive.msg_id,
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
        }
        if self.missive.model == _c.MODE_POSTALAR:
            base.update({
                "acknowledgement_of_receipt": True,
                "acknowledgement_of_receipt_scanning": False,
            })
        return base

    @property
    def user_webhook(self):
        if not self.user_cache:
            from oauth2_provider.models import Application
            self.user_cache = Application.objects.get(user__email=setting("MAILEVA_OAUTH_EMAIL"))
        return self.user_cache

    @property
    def webhook_data(self):
        return {
            "resource_type": self.resource_type,
            "callback_url": self.callback_url,
            #"authentication": {
            #    "oauth2": {
            #        "oauth2_server": MightyConfig.webhook + "/oauth2/token/",
            #        "client_id": self.user_webhook.client_id,
            #        "client_secret": setting("MAILEVA_OAUTH_SECRET"),
            #        "grant_type": "client_credentials"
            #    }
            #}
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
        return self.api_official

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
        print(response.json())
        self.access_token = response.json()["access_token"]
        return self.valid_response(response)

    def create_sending(self):
        response = requests.post(self.api_url["sendings"], headers=self.api_headers, json=self.postal_data)
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
        for event in self.events:
            wdata = self.webhook_data
            wdata["event_type"] = event
            api = self.api_url["webhook"]
            response = requests.post(api, headers=self.api_headers, json=wdata)
            self.valid_response(response)

    def on_webhook(self, request):
        key = request.GET.get("key")
        if key:
            missive = get_object_or_404(Missive, msg_id=key)
        else:
            partner_id = request.POST.get("resource_id")
            missive = get_object_or_404(Missive, partner_id=partner_id)
        missive.check_status()

    def send_postal(self):
        self.missive.msg_id = str(uuid4())
        print("okkkkkk")
        print(self.missive.mode)
        if self.missive.status == _c.STATUS_FILETEST:
            self.postal_base()
        else:
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
                if setting("MAILEVA_WEBHOOK"):
                    self.enable_webhooks()
            else:
                self.missive.to_error()
            getattr(self, "check_%s" % self.missive.mode.lower())()
            return self.missive.status