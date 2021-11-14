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
        "auth": "https://connexion.sandbox.maileva.net/auth/realms/services/protocol/openid-connect/token",
        "email": "https://test.ar24.fr/api/mail",
    }
    api_official = {
        "auth": "https://connexion.maileva.com/auth/realms/services/protocol/openid-connect/token",
        "endpoint": "https://test.ar24.fr/api/",
    }
    sending_id = None
    access_token = None
    priority = 1
    in_error = False
    fields = ["denomination", "target", "complement", "address"]

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
            "notification_email": setting("LAPOST_NOTIFICATION"),
            "archiving_duration": 0,
            "envelope_windows_type": "SIMPLE",
            "postage_type": "ECONOMIC",
        }

    @property
    def target_data(self):
        data = {
            "custom_id":  self.missive.msg_id,
            "custom_data": self.missive.msg_id,
            "address_line_6": self.missive.city,
            "country_code": self.missive.country_code.upper(),
        }
        i = 0
        for field in self.fields:
            attr = getattr(self.missive, field)
            print(i)
            print(attr)
            if attr:
                i+=1
                data["address_line_"+str(i)] = attr
        print(data)
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
        print(response)
        self.access_token = response.json()["access_token"]
        return self.valid_response(response)

    def create_sending(self):
        response = requests.post(self.api_url["sendings"], headers=self.api_headers, json=self.our_data)
        self.sending_id = response.json()["id"]
        self.missive.partner_id = self.sending_id
        return self.valid_response(response)

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
            self.postal_base()
            self.postal_attachments()
            os.remove(self.path_base_doc)
        if not self.in_error and self.submit():
            self.missive.to_sent()
        else:
            self.missive.to_error()
        self.missive.save()
        return self.missive.status
