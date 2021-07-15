from mighty.applications.messenger.backends import MissiveBackend
from mighty.functions import setting
from mighty.apps import MightyConfig
import requests, json

class MissiveBackend(MissiveBackend):
    APIFROM = setting('PAASOO_FROM', 'MIGHTY')
    APIKEY = setting('PAASOO_KEY', False)
    APISECRET = setting('PAASOO_SECRET', False)
    APIURL = "https://api.paasoo.com/json?key=%(key)s&secret=%(secret)s&from=%(from)s&to=%(to)s&text=%(text)s"
    in_error = False

    def get_api_url(self):
        return api_url % {
            "key": self.APIKEY,
            "secret": self.APISECRET,
            "from": self.APIFROM,
            "to": self.missive.target, 
            "text": self.missive.txt,
        }

    def valid_response(self, response):
        if response.status_code not in [200, 201]:
            self.missive.trace = str(response.json())
            self.in_error = True
            return False
        return True

    def send_sms(self):
        over_target = 
        self.missive.target = over_target if over_target else self.missive.target
        self.missive.status = choices.STATUS_SENT
        if setting('MISSIVE_SERVICE', False):
            api_url = self.get_api_url(self.missive)
            headers = {'accept': 'application/json'}
            response = requests.get(api_url, headers=headers)
            if self.valid_response(response):
                self.missive.msg_id = response.json()['messageid']
        if not self.in_error:
            self.missive.to_sent()
        self.missive.save()            
        return self.missive.status