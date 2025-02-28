import json

import requests

from mighty.applications.messenger import choices
from mighty.applications.messenger.backends import MissiveBackend
from mighty.functions import setting


class MissiveBackend(MissiveBackend):
    APIFROM = setting('SMSPARTNER_FROM', 'MIGHTY')
    APIKEY = setting('SMSPARTNER_KEY', False)
    APISECRET = setting('PAASOO_SECRET', False)
    APIURL = 'https://api.smspartner.fr/v1/'
    in_error = False

    @property
    def check_fields(self):
        return {
            'apiKey': self.APIKEY,
            'phoneNumber': self.missive.target,
            'messageId': self.missive.partner_id,
        }

    @property
    def post_fields(self):
        return {
            'apiKey': self.APIKEY,
            'sandbox': 0 if setting('MISSIVE_SERVICE', True) else 0,
            'sender': self.APIFROM,
            'phoneNumbers': self.missive.target,
            'message': self.missive.txt,
            'isStopSms': 0,
        }

    def valid_response(self, response):
        if response.status_code not in [200, 201]:
            self.missive.trace = str(response.json())
            self.in_error = True
            return False
        return True

    def check_sms(self):
        url = self.APIURL + 'message-status'
        r = requests.get(url, params=self.check_fields)
        r_json = r.json()
        status = r_json['statut'].lower()

        status_dict = {
            'delivered': choices.STATUS_RECEIVED,
            'not delivered': choices.STATUS_REJECTED,
            'waiting': choices.STATUS_PENDING,
            'ko': choices.STATUS_ERROR,
        }

        result = status_dict.get(status, choices.STATUS_ACCEPTED)

        self.missive.status = result
        self.missive.save()

        return json.dumps(result)

    def send_sms(self):
        over_target = setting('MISSIVE_PHONE', False)
        self.missive.target = over_target or self.missive.target
        self.missive.status = choices.STATUS_SENT
        if setting('MISSIVE_SERVICE', False):
            response = requests.post(self.APIURL + 'send', json=self.post_fields)
            if self.valid_response(response):
                self.missive.partner_id = response.json()['message_id']

        if not self.in_error:
            self.missive.to_sent()
        self.missive.save()
        return self.missive.status
