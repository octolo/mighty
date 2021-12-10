from django.core.files import File

from mighty.applications.messenger.backends import MissiveBackend
from mighty.functions import setting
from mighty.apps import MightyConfig
from django.conf import settings

from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Protocol.KDF import PBKDF2
import hashlib, base64, datetime, requests, json, os

class MissiveBackend(MissiveBackend):
    api_sandbox = {
        "email": "https://test.ar24.fr/api/mail",
        "base": "https://test.ar24.fr/api/",
        "user": "https://test.ar24.fr/api/user/",
        "confirm": "https://test.ar24.fr/api/user/request_access",
        "attachment": "https://test.ar24.fr/api/attachment/",
        "valid": "api/id_action/valid",
        "refuse": "api/id_action/refuse",
    }
    api_prod = {
        "email": "https://ar24.fr/api/mail",
        "base": "https://ar24.fr/api/",
        "user": "https://ar24.fr/api/user/",
        "confirm": "https://ar24.fr/api/user/request_access",
        "attachment": "https://ar24.fr/api/attachment/",
    }
    api_key_test = "7X9gx9E3Qx4EiUdB63nc"
    api_token = settings.AR24_TOKEN
    api_key = settings.AR24_KEY
    api_name = settings.AR24_NAME
    api_email = settings.AR24_EMAIL
    api_default = settings.AR24_DEFAULT
    in_error = False
    cache_date_send = None
    user = None
    list_attach = []
    files_attach = []
    format_date = "%Y-%m-%d %H:%M:%S" # -> YYYY-MM-DD HH:MM:SS

    __pad = lambda self,s: s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)
    __unpad = lambda self,s: s[:-ord(s[len(s) - 1:])]

    @property
    def api_url(self):
        if setting('MISSIVE_SERVICE', False):
            return self.api_sandbox
        return self.api_sandbox

    def hash_key(self, add=""):
        m = hashlib.sha256()
        key = add+self.api_key
        m.update(key.encode())
        return m.hexdigest()

    @property
    def hash_double_key(self):
        m = hashlib.sha256()
        m.update(self.hash_key().encode())
        return m.hexdigest()

    @property
    def init_vector(self):
        return self.hash_double_key[0:16]

    def generate_date_send(self):
        now = datetime.datetime.now()
        self.cache_date_send = datetime.datetime.strftime(now, self.format_date)

    @property
    def date_send(self):
        if not self.cache_date_send:
            self.generate_date_send()
        return self.cache_date_send

    @property
    def signature(self):
        return self.encrypt_data(str(self.date_send))
        
    @property
    def api_headers(self):
        return { 'accept': 'application/json', 'signature': self.signature }

    def cipher(self, iv, add=""):
        return AES.new(self.hash_key(add)[:32], AES.MODE_CBC, iv)

    def encrypt_data(self, data):
        raw = self.__pad(data)
        return base64.b64encode(self.cipher(self.init_vector).encrypt(raw))

    def decrypt_data(self, data, add=""):
        raw = base64.b64decode(data)
        return self.__unpad(self.cipher(self.init_vector, self.date_send).decrypt(raw))

    @property
    def base_headers(self):
        return { "token" : self.api_token, "date": self.date_send }

    # RESPONSE
    def valid_response(self, response):
        try:
            self.missive.trace = str(response.json())
            self.logger.info("Error: %s" % self.missive.trace)
            self.in_error = True
            return False
        except Exception:
            pass
        return True

    # CONFIRMED
    @property
    def data_confirm(self):
        data = self.base_headers
        data["email"] = "dev@easyshares.io"
        return data

    def is_confirmed(self):
        if not self.user["confirmed"] and not self.in_error:
            response = requests.post(self.api_url["user"], headers=self.api_headers, data=self.data_confirm)
            response = self.decrypt_data(response.content) if self.valid_response(response) else response.content
            if not self.in_error:
                self.logger.info("Confirmed user: %s" % response)
            return False
        return True

    # EXPEDITEUR
    @property
    def data_user(self):
        data = self.base_headers
        data.update(self.api_default)
        return data

    def create_user(self):
        self.in_error = False
        response = requests.post(self.api_url["user"], headers=self.api_headers, data=self.data_user)
        response = self.decrypt_data(response.content) if self.valid_response(response) else response.content
        self.logger.info("Create user: %s" % response)
        return response

    def get_user(self):
        response = requests.get(self.api_url["user"], headers=self.api_headers, params=self.data_user)
        response = self.decrypt_data(response.content) if self.valid_response(response) else response.content
        if self.in_error: response = self.create_user()
        self.user = json.loads(response.decode())["result"]
        self.logger.info("Get user: %s" % self.user)
        self.is_confirmed()

    # SEND AR

    def data_ar(self):
        data = self.base_headers
        data.update({
            "id_user": self.user["id"], 
            "eidas": 1,
            "to_lastname": self.missive.last_name,
            "to_firstname": self.missive.first_name,
            "to_email": self.missive.target,
            "dest_statut": "professionnel",
            "content": self.missive.html if self.missive.html else self.missive.txt,
            "to_company": "Easy-Shares",
        })
        i = 0
        for attach in self.list_attach:
            data.update({
                "attachment[%s]" % str(i): attach["file_id"]
            })
            i+=1
        print("")
        print(data)
        print("")
        return data

    def data_attachment(self, document):
        data = self.base_headers
        data.update({
            "file": open(document.name, 'rb'),
            "file_name": os.path.basename(document.name),
            "id_user": self.user["id"],
        })
        return data

    def email_attachments(self):
        if self.missive.attachments:
            for document in self.missive.attachments:
                response = requests.post(self.api_url["attachment"], 
                    headers=self.api_headers,
                    files={'file': (os.path.basename(document.name), open(document.name, 'rb'))},
                    data=self.data_attachment(document))
                response = self.decrypt_data(response.content) if self.valid_response(response) else response.content
                if not self.in_error:
                    response = json.loads(response)["result"]
                    self.list_attach.append(response)
            self.missive.logs['attachments'] = self.list_attach
        return False if self.in_error else True

    def send_email(self):
        self.get_user()
        self.generate_date_send()
        over_target = setting('MISSIVE_EMAIL', False)
        self.missive.target = over_target if over_target else self.missive.target
        self.email_attachments()
        response = requests.post(self.api_url["email"], headers=self.api_headers, data=self.data_ar())
        response = self.decrypt_data(response.content) if self.valid_response(response) else response.content
        print(response)
        if not self.in_error:
            response = json.loads(response)["result"]
            self.missive.msg_id = response["id"]
            self.missive.cache = response
            self.missive.to_sent()
        if not self.missive.in_test:
            self.missive.save()
        return self.missive.status

    def testBackend(self):
        self.missive.in_test = True
        self.missive.last_name = "Mighty-Lastname"
        self.missive.first_name = "Mighty-Firstname"
        self.missive.target = "charles@easyshares.io"
        self.missive.attachments = [open(os.path.realpath(__file__))]
        self.send_email()
        self.logger.info("Send email: %s" % self.missive.cache)