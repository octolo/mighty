from mighty.applications.messenger.partners.maileva import Maileva
from mighty.apps import MightyConfig
import os, requests

class MissiveBackend(Maileva):
    resource_type = "registered_mail/v2/sendings"
    callback_url = MightyConfig.webhook + "/wbh/messenger/postalar/"
    api_sandbox = {
        "auth": "https://connexion.sandbox.maileva.net/auth/realms/services/protocol/openid-connect/token",
        "webhook": "https://api.sandbox.maileva.net/notification_center/v2/subscriptions",
        "sendings": "https://api.sandbox.maileva.net/registered_mail/v2/sendings",
        "documents": "https://api.sandbox.maileva.net/registered_mail/v2/sendings/%s/documents",
        "recipients": "https://api.sandbox.maileva.net/registered_mail/v2/sendings/%s/recipients",
        "submit": "https://api.sandbox.maileva.net/registered_mail/v2/sendings/%s/submit",
        "webhook": "https://api.sandbox.maileva.net/notification_center/v2/subscriptions",
    }
    api_official = {
        "auth": "https://connexion.maileva.com/auth/realms/services/protocol/openid-connect/token",
        "webhook": "https://api.maileva.com/notification_center/v2/subscriptions",
        "sendings": "https://api.maileva.com/registered_mail/v2/sendings",
        "documents": "https://api.maileva.com/registered_mail/v2/sendings/%s/documents",
        "recipients": "https://api.maileva.com/registered_mail/v2/sendings/%s/recipients",
        "submit": "https://api.maileva.com/registered_mail/v2/sendings/%s/submit",
    }

    def check_postalar(self):
        self.authentication()
        url = self.api_url["sendings"] + "/" + self.missive.partner_id
        response = requests.get(url, headers=self.api_headers)
        rjson = response.json()
        self.missive.trace = str(rjson)
        if "status" in rjson:
            self.missive.status = self.status_ref[rjson["status"]]
        self.missive.save()
        return response.json()


