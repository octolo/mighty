from mighty.applications.messenger.backends.partners.maileva import Maileva
from mighty.apps import MightyConfig
import os, requests

class MissiveBackend(Maileva):
    resource_type = "mail/v2/sendings"
    callback_url = MightyConfig.webhook + "/wbh/messenger/postal/"
    api_sandbox = {
        "webhook": "https://api.sandbox.maileva.net/notification_center/v2/subscriptions",
        "auth": "https://connexion.sandbox.maileva.net/auth/realms/services/protocol/openid-connect/token",
        "sendings": "https://api.sandbox.maileva.net/mail/v2/sendings",
        "documents": "https://api.sandbox.maileva.net/mail/v2/sendings/%s/documents",
        "recipients": "https://api.sandbox.maileva.net/mail/v2/sendings/%s/recipients",
        "submit": "https://api.sandbox.maileva.net/mail/v2/sendings/%s/submit",
    }
    api_official = {
        "webhook": "https://api.maileva.com/notification_center/v2/subscriptions",
        "auth": "https://connexion.maileva.com/auth/realms/services/protocol/openid-connect/token",
        "sendings": "https://api.maileva.com/mail/v2/sendings",
        "documents": "https://api.maileva.com/mail/v2/sendings/%s/documents",
        "recipients": "https://api.maileva.com/mail/v2/sendings/%s/recipients",
        "submit": "https://api.maileva.com/mail/v2/sendings/%s/submit",
    }

    def check_postal(self):
        if self.authentication():
            url = self.api_url["sendings"] + "/" + self.missive.partner_id
            response = requests.get(url, headers=self.api_headers)
            rjson = response.json()
            self.missive.trace = str(rjson)
            if "status" in rjson:
                self.missive.status = self.status_ref[rjson["status"]]
            self.missive.save()
            return rjson

