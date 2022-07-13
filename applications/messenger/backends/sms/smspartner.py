from mighty.applications.messenger.backends import MissiveBackend
from mighty.functions import setting
from mighty.apps import MightyConfig
from mighty.applications.messenger import choices
import requests, json

class MissiveBackend(MissiveBackend):
    APIFROM = setting('SMSPARTNER_FROM', 'MIGHTY')
    APIKEY = setting('SMSPARTNER_KEY', False)
    APISECRET = setting('PAASOO_SECRET', False)
    APIURL = "https://api.smspartner.fr/v1/send"
    in_error = False

    @property
    def post_fields(self):
        return {
            "apiKey": self.APIKEY,
            "sandbox": 0 if setting('MISSIVE_SERVICE', True) else 0,
            "sender": self.APIFROM,
            "phoneNumbers": self.missive.target, 
            "message": self.missive.txt,
        }

    def valid_response(self, response):
        if response.status_code not in [200, 201]:
            self.missive.trace = str(response.json())
            self.in_error = True
            return False
        return True

    def send_sms(self):
        over_target = setting('MISSIVE_PHONE', False)
        self.missive.target = over_target if over_target else self.missive.target
        self.missive.status = choices.STATUS_SENT
        response = requests.post(self.APIURL, json=self.post_fields)
        if self.valid_response(response):
            self.missive.msg_id = response.json()['message_id']
        if not self.in_error:
            self.missive.to_sent()
        self.missive.save()            
        return self.missive.status