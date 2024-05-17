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
        from datetime import datetime
        self.priority+=1
        api = self.api_url["documents"] % self.sending_id
        headers = self.api_headers
        doc_name = os.path.basename(attachment.name)

        # Define the boundary for the multipart form-data
        boundary = f"----------------------------{hex(int(datetime.now().timestamp()))[2:]}"
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"

        # Prepare the multipart form-data content
        file_bytes = attachment.read()

        file_content_disposition = f'form-data; name="document"; filename="{doc_name}"'
        metadata_json = json.dumps({"priority": self.priority, "name": doc_name})

        data = (
            f"--{boundary}\r\n"
            f"Content-Disposition: {file_content_disposition}\r\n"
            f"Content-Type: application/octet-stream\r\n\r\n"
            f"{file_bytes.decode('ISO-8859-1')}\r\n"
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"metadata\"\r\n"
            f"Content-Type: application/json\r\n\r\n"
            f"{metadata_json}\r\n"
            f"--{boundary}--\r\n"
        )

        response = requests.post(api, headers=headers, data=data)

        print(response.text)
        self.valid_response(response)
        self.add_log_array("attachments", doc_name)


    def postal_attachments(self):
        if self.missive.attachments:
            for document in self.missive.attachments:
                self.postal_add_attachment(document)
        return False if self.in_error else True


