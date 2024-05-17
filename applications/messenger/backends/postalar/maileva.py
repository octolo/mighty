from mighty.applications.messenger.backends.partners.maileva import Maileva
from mighty.apps import MightyConfig
import os, requests, json

class MissiveBackend(Maileva):
    resource_type = "registered_mail/v4/sendings"
    callback_url = MightyConfig.webhook + "/wbh/messenger/postalar/"
    api_sandbox = {
        "webhook": "https://api.sandbox.maileva.net/notification_center/v4/subscriptions",
        "auth": "https://connexion.sandbox.maileva.net/auth/realms/services/protocol/openid-connect/token",
        "sendings": "https://api.sandbox.maileva.net/registered_mail/v4/sendings",
        "documents": "https://api.sandbox.maileva.net/registered_mail/v4/sendings/%s/documents",
        "recipients": "https://api.sandbox.maileva.net/registered_mail/v4/sendings/%s/recipients",
        "submit": "https://api.sandbox.maileva.net/registered_mail/v4/sendings/%s/submit",
    }
    api_official = {
        "webhook": "https://api.maileva.com/notification_center/v4/subscriptions",
        "auth": "https://connexion.maileva.com/auth/realms/services/protocol/openid-connect/token",
        "sendings": "https://api.maileva.com/registered_mail/v4/sendings",
        "documents": "https://api.maileva.com/registered_mail/v4/sendings/%s/documents",
        "recipients": "https://api.maileva.com/registered_mail/v4/sendings/%s/recipients",
        "submit": "https://api.maileva.com/registered_mail/v4/sendings/%s/submit",
    }

    def check_postalar(self):
        if self.authentication():
            url = self.api_url["sendings"] + "/" + self.missive.partner_id
            response = requests.get(url, headers=self.api_headers)
            rjson = response.json()
            self.missive.trace = str(rjson)
            if "status" in rjson:
                self.missive.status = self.status_ref[rjson["status"]]
            self.missive.save()
            return rjson

    def postal_add_attachment(self, attachment):
        self._logger.info("postal_add_attachment %s" % attachment.name)
        self.priority+=1
        api = self.api_url["documents"] % self.sending_id
        headers = self.api_headers
        doc_name = os.path.basename(attachment.name)
        data = { "priority": self.priority, "name": doc_name, "shrink": True}
        files = {
            'document': (doc_name, open(attachment.name, "rb").read().decode('ISO-8859-1')),
            "metadata": ("metadata", json.dumps(data), "application/json"),
        }
        response = requests.post(api, headers=headers, files=files)
        self.valid_response(response)
        self.add_log_array("attachments", doc_name)


    def postal_attachments(self):
        if self.missive.attachments:
            import tempfile, os
            from django.utils.text import get_valid_filename
            for document in self.missive.attachments:
                suffix = get_valid_filename(os.path.basename(str(document)))
                with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_pdf:
                    tmp_pdf.write(document.read())
                    self.postal_add_attachment(tmp_pdf)
        return False if self.in_error else True

